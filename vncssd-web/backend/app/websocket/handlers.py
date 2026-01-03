"""
VNCSSDetector Web Service - WebSocket Handlers
"""
import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, Optional, Set

from fastapi import WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import async_session_maker
from app.models.node import Node, NodeStatus
from app.services.node_service import NodeService

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections for nodes and dashboard clients."""
    
    def __init__(self):
        # Node connections: uuid -> WebSocket
        self.node_connections: Dict[str, WebSocket] = {}
        # Dashboard connections: Set of WebSockets
        self.dashboard_connections: Set[WebSocket] = set()
        # Node data cache: uuid -> latest stats
        self.node_stats_cache: Dict[str, dict] = {}
    
    async def connect_node(self, websocket: WebSocket, node_uuid: str) -> bool:
        """Accept a node connection."""
        await websocket.accept()
        self.node_connections[node_uuid] = websocket
        logger.info(f"Node {node_uuid} connected")
        
        # Update node status
        async with async_session_maker() as db:
            node = await NodeService.get_node_by_uuid(db, node_uuid)
            if node:
                await NodeService.update_node_status(db, node, NodeStatus.ONLINE)
                await db.commit()
        
        # Notify dashboard clients
        await self.broadcast_to_dashboards({
            "type": "node_connected",
            "node_uuid": node_uuid,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        return True
    
    async def disconnect_node(self, node_uuid: str):
        """Handle node disconnection."""
        if node_uuid in self.node_connections:
            del self.node_connections[node_uuid]
        
        if node_uuid in self.node_stats_cache:
            del self.node_stats_cache[node_uuid]
        
        logger.info(f"Node {node_uuid} disconnected")
        
        # Update node status
        async with async_session_maker() as db:
            node = await NodeService.get_node_by_uuid(db, node_uuid)
            if node:
                await NodeService.update_node_status(db, node, NodeStatus.OFFLINE)
                await db.commit()
        
        # Notify dashboard clients
        await self.broadcast_to_dashboards({
            "type": "node_disconnected",
            "node_uuid": node_uuid,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    async def connect_dashboard(self, websocket: WebSocket):
        """Accept a dashboard connection."""
        await websocket.accept()
        self.dashboard_connections.add(websocket)
        logger.info(f"Dashboard client connected (total: {len(self.dashboard_connections)})")
        
        # Send current state
        await websocket.send_json({
            "type": "initial_state",
            "connected_nodes": list(self.node_connections.keys()),
            "node_stats": self.node_stats_cache
        })
    
    async def disconnect_dashboard(self, websocket: WebSocket):
        """Handle dashboard disconnection."""
        self.dashboard_connections.discard(websocket)
        logger.info(f"Dashboard client disconnected (total: {len(self.dashboard_connections)})")
    
    async def broadcast_to_dashboards(self, message: dict):
        """Broadcast a message to all dashboard clients."""
        disconnected = set()
        
        for ws in self.dashboard_connections:
            try:
                await ws.send_json(message)
            except Exception:
                disconnected.add(ws)
        
        # Clean up disconnected clients
        self.dashboard_connections -= disconnected
    
    async def send_to_node(self, node_uuid: str, message: dict) -> bool:
        """Send a message to a specific node."""
        if node_uuid not in self.node_connections:
            return False
        
        try:
            await self.node_connections[node_uuid].send_json(message)
            return True
        except Exception:
            await self.disconnect_node(node_uuid)
            return False
    
    def update_node_stats(self, node_uuid: str, stats: dict):
        """Update cached stats for a node."""
        self.node_stats_cache[node_uuid] = {
            **stats,
            "last_updated": datetime.utcnow().isoformat()
        }
    
    def is_node_connected(self, node_uuid: str) -> bool:
        """Check if a node is connected."""
        return node_uuid in self.node_connections


# Global connection manager
manager = ConnectionManager()


class NodeWebSocketHandler:
    """Handler for node WebSocket connections."""
    
    @staticmethod
    async def handle_connection(websocket: WebSocket, node_uuid: str, api_key: str):
        """Handle a node WebSocket connection."""
        # Authenticate node
        async with async_session_maker() as db:
            node = await NodeService.authenticate_node(db, node_uuid, api_key)
            if not node:
                await websocket.close(code=4001, reason="Authentication failed")
                return
        
        # Connect node
        await manager.connect_node(websocket, node_uuid)
        
        try:
            while True:
                # Receive message from node
                data = await websocket.receive_json()
                await NodeWebSocketHandler.process_node_message(node_uuid, data)
                
        except WebSocketDisconnect:
            await manager.disconnect_node(node_uuid)
        except Exception as e:
            logger.error(f"Error handling node {node_uuid}: {e}")
            await manager.disconnect_node(node_uuid)
    
    @staticmethod
    async def process_node_message(node_uuid: str, data: dict):
        """Process a message from a node."""
        msg_type = data.get("type")
        
        if msg_type == "stats":
            # System stats update
            manager.update_node_stats(node_uuid, data.get("data", {}))
            await manager.broadcast_to_dashboards({
                "type": "node_stats",
                "node_uuid": node_uuid,
                "data": data.get("data", {})
            })
        
        elif msg_type == "recording_started":
            await manager.broadcast_to_dashboards({
                "type": "recording_started",
                "node_uuid": node_uuid,
                "recording_name": data.get("recording_name"),
                "timestamp": datetime.utcnow().isoformat()
            })
        
        elif msg_type == "recording_stopped":
            await manager.broadcast_to_dashboards({
                "type": "recording_stopped",
                "node_uuid": node_uuid,
                "recording_name": data.get("recording_name"),
                "timestamp": datetime.utcnow().isoformat()
            })
        
        elif msg_type == "warning_detected":
            # Analysis warning
            await manager.broadcast_to_dashboards({
                "type": "warning_detected",
                "node_uuid": node_uuid,
                "warning": data.get("warning", {}),
                "timestamp": datetime.utcnow().isoformat()
            })
            
            # Create alert in database
            async with async_session_maker() as db:
                from app.models.alert import Alert, AlertSeverity
                
                node = await NodeService.get_node_by_uuid(db, node_uuid)
                if node:
                    alert = Alert(
                        node_id=node.id,
                        severity=AlertSeverity.HIGH,
                        title=data.get("warning", {}).get("title", "Warning Detected"),
                        description=data.get("warning", {}).get("message", "")
                    )
                    db.add(alert)
                    await db.commit()
        
        elif msg_type == "log":
            # Log message from node
            async with async_session_maker() as db:
                from app.models.log import SystemLog, LogLevel
                
                node = await NodeService.get_node_by_uuid(db, node_uuid)
                if node:
                    log = SystemLog(
                        node_id=node.id,
                        level=LogLevel(data.get("level", "info")),
                        source=data.get("source", "node"),
                        message=data.get("message", ""),
                        extra_data=data.get("metadata")
                    )
                    db.add(log)
                    await db.commit()
        
        elif msg_type == "heartbeat":
            # Update last seen
            async with async_session_maker() as db:
                node = await NodeService.get_node_by_uuid(db, node_uuid)
                if node:
                    node.last_seen_at = datetime.utcnow()
                    await db.commit()


class DashboardWebSocketHandler:
    """Handler for dashboard WebSocket connections."""
    
    @staticmethod
    async def handle_connection(websocket: WebSocket):
        """Handle a dashboard WebSocket connection."""
        await manager.connect_dashboard(websocket)
        
        try:
            while True:
                # Receive message from dashboard
                data = await websocket.receive_json()
                await DashboardWebSocketHandler.process_dashboard_message(websocket, data)
                
        except WebSocketDisconnect:
            await manager.disconnect_dashboard(websocket)
        except Exception as e:
            logger.error(f"Error handling dashboard: {e}")
            await manager.disconnect_dashboard(websocket)
    
    @staticmethod
    async def process_dashboard_message(websocket: WebSocket, data: dict):
        """Process a message from a dashboard client."""
        msg_type = data.get("type")
        
        if msg_type == "send_to_node":
            # Forward message to a node
            node_uuid = data.get("node_uuid")
            message = data.get("message", {})
            
            success = await manager.send_to_node(node_uuid, message)
            await websocket.send_json({
                "type": "command_result",
                "node_uuid": node_uuid,
                "success": success
            })
        
        elif msg_type == "request_node_stats":
            # Request stats from all connected nodes
            for node_uuid in manager.node_connections.keys():
                await manager.send_to_node(node_uuid, {"type": "request_stats"})
