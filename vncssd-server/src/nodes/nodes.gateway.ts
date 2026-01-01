import {
    WebSocketGateway,
    WebSocketServer,
    SubscribeMessage,
    OnGatewayConnection,
    OnGatewayDisconnect,
    MessageBody,
    ConnectedSocket,
} from '@nestjs/websockets';
import { Server, Socket } from 'socket.io';
import { JwtService } from '@nestjs/jwt';
import { ConfigService } from '@nestjs/config';
import { NodesService } from './nodes.service';
import { EventsService } from '../events/events.service';

// Message types for Node↔Server protocol
export interface NodeMessage {
    msg_type: string;
    msg_id: string;
    timestamp: string;
    node_id?: string;
    payload: Record<string, unknown>;
}

interface NodeSocket extends Socket {
    nodeId?: string;
    nodeKey?: string;
}

@WebSocketGateway({
    namespace: '/nodes',
    cors: {
        origin: '*',
    },
})
export class NodesGateway implements OnGatewayConnection, OnGatewayDisconnect {
    @WebSocketServer()
    server: Server;

    private connectedNodes = new Map<string, NodeSocket>();

    constructor(
        private jwtService: JwtService,
        private configService: ConfigService,
        private nodesService: NodesService,
        private eventsService: EventsService,
    ) { }

    async handleConnection(client: NodeSocket) {
        try {
            // Extract JWT from handshake
            const token =
                client.handshake.auth?.token ||
                client.handshake.headers?.authorization?.replace('Bearer ', '');

            if (!token) {
                this.sendError(client, 'AUTH_REQUIRED', 'Authentication required');
                client.disconnect();
                return;
            }

            // Verify JWT (signed with node secret)
            const payload = this.jwtService.verify(token, {
                secret: this.configService.get('NODE_JWT_SECRET'),
            });

            const node = await this.nodesService.getNodeByKey(payload.nodeKey);
            if (!node) {
                this.sendError(client, 'NODE_NOT_FOUND', 'Node not registered');
                client.disconnect();
                return;
            }

            // Store node info on socket
            client.nodeId = node.id;
            client.nodeKey = node.nodeKey;

            // Join room for this node
            client.join(`node:${node.id}`);

            // Track connected node
            this.connectedNodes.set(node.id, client);

            // Send connected acknowledgment
            this.send(client, 'CONNECTED', {
                session_id: client.id,
                server_time: new Date().toISOString(),
            });

            console.log(`Node connected: ${node.hostname} (${node.id})`);
        } catch (error) {
            console.error('Node connection error:', error);
            this.sendError(client, 'AUTH_FAILED', 'Authentication failed');
            client.disconnect();
        }
    }

    async handleDisconnect(client: NodeSocket) {
        if (client.nodeId) {
            this.connectedNodes.delete(client.nodeId);
            await this.nodesService.markOffline(client.nodeId);
            console.log(`Node disconnected: ${client.nodeId}`);
        }
    }

    @SubscribeMessage('REGISTER')
    async handleRegister(
        @MessageBody() message: NodeMessage,
        @ConnectedSocket() client: NodeSocket,
    ) {
        if (!client.nodeKey) {
            return this.sendError(client, 'NOT_AUTHENTICATED', 'Not authenticated');
        }

        const { payload } = message;

        await this.nodesService.registerNode(client.nodeKey, {
            hostname: payload.hostname as string,
            ipAddress: payload.ip_address as string,
            os: payload.os as string,
            version: payload.version as string,
            capabilities: payload.capabilities as string[],
            metadata: payload.metadata as Record<string, unknown>,
        });

        this.send(client, 'REGISTERED', {
            status: 'ok',
            config: {
                heartbeat_interval_ms: 30000,
                telemetry_interval_ms: 60000,
            },
        });
    }

    @SubscribeMessage('HEARTBEAT')
    async handleHeartbeat(
        @MessageBody() message: NodeMessage,
        @ConnectedSocket() client: NodeSocket,
    ) {
        if (!client.nodeId) {
            return this.sendError(client, 'NOT_AUTHENTICATED', 'Not authenticated');
        }

        const metrics = message.payload as Record<string, unknown>;

        await this.nodesService.updateHeartbeat(client.nodeId, metrics);

        this.send(client, 'HEARTBEAT_ACK', {
            server_time: new Date().toISOString(),
        });
    }

    @SubscribeMessage('TELEMETRY')
    async handleTelemetry(
        @MessageBody() message: NodeMessage,
        @ConnectedSocket() client: NodeSocket,
    ) {
        if (!client.nodeId) {
            return this.sendError(client, 'NOT_AUTHENTICATED', 'Not authenticated');
        }

        const { metrics } = message.payload as { metrics: Record<string, unknown> };

        await this.nodesService.updateHeartbeat(client.nodeId, metrics);

        // Acknowledge telemetry
        this.send(client, 'TELEMETRY_ACK', { msg_id: message.msg_id });
    }

    @SubscribeMessage('EVENT')
    async handleEvent(
        @MessageBody() message: NodeMessage,
        @ConnectedSocket() client: NodeSocket,
    ) {
        if (!client.nodeId) {
            return this.sendError(client, 'NOT_AUTHENTICATED', 'Not authenticated');
        }

        const { event_type, severity, message: eventMessage, data } = message.payload;

        await this.eventsService.createEvent(client.nodeId, {
            eventType: event_type as string,
            severity: severity as string,
            message: eventMessage as string,
            data: data as Record<string, unknown>,
        });

        // Acknowledge event
        this.send(client, 'EVENT_ACK', { msg_id: message.msg_id });
    }

    @SubscribeMessage('COMMAND_ACK')
    async handleCommandAck(
        @MessageBody() message: NodeMessage,
        @ConnectedSocket() client: NodeSocket,
    ) {
        if (!client.nodeId) {
            return;
        }

        const { command_id, status } = message.payload;
        await this.eventsService.updateCommandStatus(
            command_id as string,
            status as string,
        );
    }

    @SubscribeMessage('COMMAND_RESULT')
    async handleCommandResult(
        @MessageBody() message: NodeMessage,
        @ConnectedSocket() client: NodeSocket,
    ) {
        if (!client.nodeId) {
            return;
        }

        const { command_id, status, result } = message.payload;
        await this.eventsService.saveCommandResult(
            command_id as string,
            status as string,
            result as Record<string, unknown>,
        );
    }

    /**
     * Handle ALERT message from VNCSSDetector
     * This is for IMSI-catcher detection alerts
     */
    @SubscribeMessage('ALERT')
    async handleAlert(
        @MessageBody() message: NodeMessage,
        @ConnectedSocket() client: NodeSocket,
    ) {
        if (!client.nodeId) {
            return this.sendError(client, 'NOT_AUTHENTICATED', 'Not authenticated');
        }

        const { alert_type, alert_message, data } = message.payload;

        console.log(`[ALERT] Node ${client.nodeId}: ${alert_type} - ${alert_message}`);

        // Create event for the alert
        await this.eventsService.createEvent(client.nodeId, {
            eventType: alert_type as string,
            severity: this.getAlertSeverity(alert_type as string),
            message: alert_message as string,
            data: data as Record<string, unknown>,
        });

        // Acknowledge the alert
        this.send(client, 'ALERT_ACK', {
            msg_id: message.msg_id,
            status: 'received',
        });
    }

    private getAlertSeverity(alertType: string): string {
        switch (alertType) {
            case 'IMSI_CATCHER_DETECTED':
            case 'ROGUE_BASE_STATION':
                return 'CRITICAL';
            case 'DOWNGRADE_ATTACK':
                return 'HIGH';
            case 'SIGNAL_ANOMALY':
                return 'MEDIUM';
            case 'IMSI_CATCHER_CLEARED':
            default:
                return 'LOW';
        }
    }

    // Send command to a specific node
    async sendCommand(nodeId: string, command: Record<string, unknown>) {
        const client = this.connectedNodes.get(nodeId);
        if (!client) {
            return { success: false, error: 'Node not connected' };
        }

        this.send(client, 'COMMAND', command);
        return { success: true };
    }

    // Helper methods
    private send(client: Socket, msgType: string, payload: Record<string, unknown>) {
        client.emit('message', {
            msg_type: msgType,
            msg_id: this.generateMsgId(),
            timestamp: new Date().toISOString(),
            payload,
        });
    }

    private sendError(client: Socket, code: string, message: string) {
        this.send(client, 'ERROR', { code, message });
    }

    private generateMsgId(): string {
        return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    }

    // Get online node count
    getOnlineNodeCount(): number {
        return this.connectedNodes.size;
    }

    // Check if node is online
    isNodeOnline(nodeId: string): boolean {
        return this.connectedNodes.has(nodeId);
    }
}
