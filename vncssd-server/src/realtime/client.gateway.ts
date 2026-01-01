import {
    WebSocketGateway,
    WebSocketServer,
    OnGatewayInit,
    OnGatewayConnection,
    OnGatewayDisconnect,
} from '@nestjs/websockets';
import { Server, Socket } from 'socket.io';
import { Logger, Injectable } from '@nestjs/common';
import { PrismaService } from '../prisma';

interface NodeStatusUpdate {
    id: string;
    hostname: string;
    status: string;
    latitude: number | null;
    longitude: number | null;
    locationName: string | null;
    lastSeen: Date | null;
}

interface StatusSummary {
    total: number;
    online: number;
    offline: number;
    degraded: number;
    pending: number;
}

@Injectable()
@WebSocketGateway({
    namespace: 'client',
    cors: {
        origin: '*',
    },
})
export class ClientGateway
    implements OnGatewayInit, OnGatewayConnection, OnGatewayDisconnect {
    @WebSocketServer()
    server: Server;

    private logger = new Logger('ClientGateway');
    private updateInterval: NodeJS.Timeout | null = null;
    private connectedClients = new Map<string, { workspaceId?: string }>();

    constructor(private prisma: PrismaService) { }

    afterInit() {
        this.logger.log('Client WebSocket Gateway initialized');
        this.startRealtimeUpdates();
    }

    handleConnection(client: Socket) {
        const workspaceId = client.handshake.query.workspaceId as string;
        this.connectedClients.set(client.id, { workspaceId });

        if (workspaceId) {
            client.join(`workspace:${workspaceId}`);
        }

        this.logger.log(`Client connected: ${client.id} (workspace: ${workspaceId || 'none'})`);

        // Send immediate update on connect
        this.sendNodeStatusToClient(client, workspaceId);
    }

    handleDisconnect(client: Socket) {
        this.connectedClients.delete(client.id);
        this.logger.log(`Client disconnected: ${client.id}`);
    }

    /**
     * Start sending updates every 3 seconds
     */
    private startRealtimeUpdates() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
        }

        this.updateInterval = setInterval(async () => {
            if (this.connectedClients.size === 0) return;

            await this.broadcastNodeStatus();
        }, 3000);
    }

    /**
     * Broadcast node status to all connected clients
     */
    private async broadcastNodeStatus() {
        // Get all unique workspace IDs
        const workspaceIds = new Set<string>();
        this.connectedClients.forEach((data) => {
            if (data.workspaceId) {
                workspaceIds.add(data.workspaceId);
            }
        });

        // Fetch and broadcast for each workspace
        for (const workspaceId of workspaceIds) {
            try {
                const { nodes, summary } = await this.getNodeStatusForWorkspace(workspaceId);
                this.server
                    .to(`workspace:${workspaceId}`)
                    .emit('node:status', { nodes, summary, timestamp: new Date() });
            } catch (error) {
                this.logger.error(`Failed to broadcast to workspace ${workspaceId}:`, error);
            }
        }
    }

    /**
     * Send node status to a single client
     */
    private async sendNodeStatusToClient(client: Socket, workspaceId?: string) {
        if (!workspaceId) return;

        try {
            const { nodes, summary } = await this.getNodeStatusForWorkspace(workspaceId);
            client.emit('node:status', { nodes, summary, timestamp: new Date() });
        } catch (error) {
            this.logger.error(`Failed to send status to client:`, error);
        }
    }

    /**
     * Get node status for a workspace
     */
    private async getNodeStatusForWorkspace(workspaceId: string): Promise<{
        nodes: NodeStatusUpdate[];
        summary: StatusSummary;
    }> {
        const dbNodes = await this.prisma.node.findMany({
            where: { workspaceId },
            select: {
                id: true,
                hostname: true,
                status: true,
                latitude: true,
                longitude: true,
                locationName: true,
                lastSeen: true,
            },
        });

        const nodes: NodeStatusUpdate[] = dbNodes.map((n) => ({
            id: n.id,
            hostname: n.hostname,
            status: n.status,
            latitude: n.latitude,
            longitude: n.longitude,
            locationName: n.locationName,
            lastSeen: n.lastSeen,
        }));

        const summary: StatusSummary = {
            total: nodes.length,
            online: nodes.filter((n) => n.status === 'ONLINE').length,
            offline: nodes.filter((n) => n.status === 'OFFLINE').length,
            degraded: nodes.filter((n) => n.status === 'DEGRADED').length,
            pending: nodes.filter((n) => n.status === 'PENDING').length,
        };

        return { nodes, summary };
    }

    /**
     * Manually trigger an update (called when node status changes)
     */
    async notifyNodeChange(workspaceId: string) {
        try {
            const { nodes, summary } = await this.getNodeStatusForWorkspace(workspaceId);
            this.server
                .to(`workspace:${workspaceId}`)
                .emit('node:status', { nodes, summary, timestamp: new Date() });
        } catch (error) {
            this.logger.error(`Failed to notify node change:`, error);
        }
    }
}
