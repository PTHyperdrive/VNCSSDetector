import { Injectable, Logger } from '@nestjs/common';
import { PrismaService } from '../prisma';
import { NotificationsService } from '../notifications/notifications.service';
import { ClientGateway } from '../realtime/client.gateway';

// Alert types from VNCSSDetector
export enum VNCSSAlertType {
    IMSI_CATCHER_DETECTED = 'IMSI_CATCHER_DETECTED',
    IMSI_CATCHER_CLEARED = 'IMSI_CATCHER_CLEARED',
    SIGNAL_ANOMALY = 'SIGNAL_ANOMALY',
    ROGUE_BASE_STATION = 'ROGUE_BASE_STATION',
    DOWNGRADE_ATTACK = 'DOWNGRADE_ATTACK',
}

// Alert severity mapping
const alertSeverity: Record<VNCSSAlertType, string> = {
    [VNCSSAlertType.IMSI_CATCHER_DETECTED]: 'CRITICAL',
    [VNCSSAlertType.IMSI_CATCHER_CLEARED]: 'LOW',
    [VNCSSAlertType.SIGNAL_ANOMALY]: 'MEDIUM',
    [VNCSSAlertType.ROGUE_BASE_STATION]: 'CRITICAL',
    [VNCSSAlertType.DOWNGRADE_ATTACK]: 'HIGH',
};

export interface VNCSSAlert {
    alertType: VNCSSAlertType;
    message: string;
    data?: {
        frequency?: number;
        signalStrength?: number;
        cellId?: string;
        lac?: number;
        mcc?: string;
        mnc?: string;
        detectionConfidence?: number;
        [key: string]: unknown;
    };
}

@Injectable()
export class AlertsService {
    private readonly logger = new Logger('AlertsService');

    // Track active threats per node
    private activeThreats = new Map<string, VNCSSAlert>();

    constructor(
        private prisma: PrismaService,
        private notificationsService: NotificationsService,
        private clientGateway: ClientGateway,
    ) { }

    /**
     * Process alert from VNCSSDetector node
     */
    async processNodeAlert(
        nodeId: string,
        workspaceId: string,
        alert: VNCSSAlert,
    ) {
        this.logger.warn(
            `[ALERT] Node ${nodeId}: ${alert.alertType} - ${alert.message}`,
        );

        // Get node with location
        const node = await this.prisma.node.findUnique({
            where: { id: nodeId },
            select: {
                id: true,
                hostname: true,
                latitude: true,
                longitude: true,
                locationName: true,
                workspaceId: true,
            },
        });

        if (!node) {
            this.logger.error(`Node ${nodeId} not found`);
            return;
        }

        // Store event in database
        const event = await this.prisma.nodeEvent.create({
            data: {
                nodeId,
                eventType: alert.alertType,
                severity: alertSeverity[alert.alertType] as any,
                message: alert.message,
                data: alert.data as any,
            },
        });

        // Update active threats tracking
        if (alert.alertType === VNCSSAlertType.IMSI_CATCHER_DETECTED ||
            alert.alertType === VNCSSAlertType.ROGUE_BASE_STATION) {
            this.activeThreats.set(nodeId, alert);

            // Update node metadata to mark as alerting
            await this.prisma.node.update({
                where: { id: nodeId },
                data: {
                    metadata: {
                        isAlerting: true,
                        lastAlertType: alert.alertType,
                        lastAlertTime: new Date().toISOString(),
                    },
                },
            });

            // Notify all workspace users about the threat
            await this.notifyWorkspaceUsers(node, alert);

            // Broadcast to connected clients via WebSocket
            this.clientGateway.notifyNodeChange(workspaceId);
        }

        // Clear threat if IMSI catcher is no longer detected
        if (alert.alertType === VNCSSAlertType.IMSI_CATCHER_CLEARED) {
            this.activeThreats.delete(nodeId);

            await this.prisma.node.update({
                where: { id: nodeId },
                data: {
                    metadata: {
                        isAlerting: false,
                        clearedTime: new Date().toISOString(),
                    },
                },
            });
        }

        return event;
    }

    /**
     * Notify users in the workspace about a threat
     */
    private async notifyWorkspaceUsers(
        node: {
            id: string;
            hostname: string;
            latitude: number | null;
            longitude: number | null;
            locationName: string | null;
            workspaceId: string;
        },
        alert: VNCSSAlert,
    ) {
        // Get all users in workspace
        const workspaceUsers = await this.prisma.userWorkspace.findMany({
            where: { workspaceId: node.workspaceId },
            select: { userId: true },
        });

        const userIds = workspaceUsers.map((u) => u.userId);

        // Compose warning message
        const location = node.locationName ||
            (node.latitude && node.longitude
                ? `${node.latitude.toFixed(4)}, ${node.longitude.toFixed(4)}`
                : 'Unknown location');

        const title = '⚠️ IMSI-Catcher Detected';
        const body = `WARNING: ${alert.message}\n\nLocation: ${location}\n\nThis area may not be safe. Beware of SMS fraud and avoid sensitive communications.`;

        // Send FCM push notification to all users
        for (const userId of userIds) {
            try {
                await this.notificationsService.sendPushToUser(userId, {
                    title,
                    body,
                    data: {
                        screen: 'NODE_DETAIL',
                        node_id: node.id,
                        alert_type: alert.alertType,
                        latitude: node.latitude?.toString() || '',
                        longitude: node.longitude?.toString() || '',
                    },
                });
            } catch (error) {
                this.logger.error(`Failed to notify user ${userId}:`, error);
            }
        }
    }

    /**
     * Check if client is in range of any active threat
     */
    async checkClientProximity(
        clientLat: number,
        clientLng: number,
        radiusKm: number = 1, // Default 1km radius
    ): Promise<{
        isInDanger: boolean;
        nearbyThreats: Array<{
            nodeId: string;
            hostname: string;
            distance: number;
            alertType: string;
        }>;
    }> {
        const nearbyThreats: Array<{
            nodeId: string;
            hostname: string;
            distance: number;
            alertType: string;
        }> = [];

        // Get all nodes with active threats
        const alertingNodes = await this.prisma.node.findMany({
            where: {
                id: { in: Array.from(this.activeThreats.keys()) },
                latitude: { not: null },
                longitude: { not: null },
            },
            select: {
                id: true,
                hostname: true,
                latitude: true,
                longitude: true,
            },
        });

        for (const node of alertingNodes) {
            if (!node.latitude || !node.longitude) continue;

            const distance = this.calculateDistance(
                clientLat,
                clientLng,
                node.latitude,
                node.longitude,
            );

            if (distance <= radiusKm) {
                const alert = this.activeThreats.get(node.id);
                nearbyThreats.push({
                    nodeId: node.id,
                    hostname: node.hostname,
                    distance: Math.round(distance * 1000), // meters
                    alertType: alert?.alertType || 'UNKNOWN',
                });
            }
        }

        return {
            isInDanger: nearbyThreats.length > 0,
            nearbyThreats,
        };
    }

    /**
     * Calculate distance between two coordinates (Haversine formula)
     */
    private calculateDistance(
        lat1: number,
        lon1: number,
        lat2: number,
        lon2: number,
    ): number {
        const R = 6371; // Earth's radius in km
        const dLat = this.toRad(lat2 - lat1);
        const dLon = this.toRad(lon2 - lon1);
        const a =
            Math.sin(dLat / 2) * Math.sin(dLat / 2) +
            Math.cos(this.toRad(lat1)) *
            Math.cos(this.toRad(lat2)) *
            Math.sin(dLon / 2) *
            Math.sin(dLon / 2);
        const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
        return R * c;
    }

    private toRad(deg: number): number {
        return deg * (Math.PI / 180);
    }

    /**
     * Get current active threats
     */
    getActiveThreats() {
        return Array.from(this.activeThreats.entries()).map(([nodeId, alert]) => ({
            nodeId,
            ...alert,
        }));
    }
}
