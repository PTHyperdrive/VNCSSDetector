import { Injectable } from '@nestjs/common';
import { PrismaService } from '../prisma';
import { FcmService } from './fcm.service';
import { QueryNotificationsDto } from './dto';

@Injectable()
export class NotificationsService {
    constructor(
        private prisma: PrismaService,
        private fcmService: FcmService,
    ) { }

    async registerDevice(userId: string, fcmToken: string, deviceInfo?: string) {
        // Upsert device token
        return this.prisma.deviceToken.upsert({
            where: { fcmToken },
            update: { userId, deviceInfo, updatedAt: new Date() },
            create: { userId, fcmToken, deviceInfo },
        });
    }

    async unregisterDevice(fcmToken: string) {
        return this.prisma.deviceToken.deleteMany({
            where: { fcmToken },
        });
    }

    async findAll(userId: string, query: QueryNotificationsDto) {
        const { isRead, page = 1, limit = 20 } = query;
        const skip = (page - 1) * limit;

        const where = {
            userId,
            ...(isRead !== undefined && { isRead }),
        };

        const [notifications, total, unreadCount] = await Promise.all([
            this.prisma.notification.findMany({
                where,
                skip,
                take: limit,
                orderBy: { sentAt: 'desc' },
            }),
            this.prisma.notification.count({ where }),
            this.prisma.notification.count({
                where: { userId, isRead: false },
            }),
        ]);

        return {
            notifications: notifications.map((n) => ({
                id: n.id.toString(),
                title: n.title,
                body: n.body,
                type: n.type,
                data: n.data,
                isRead: n.isRead,
                sentAt: n.sentAt,
            })),
            unreadCount,
            pagination: {
                page,
                limit,
                total,
                totalPages: Math.ceil(total / limit),
            },
        };
    }

    async markAsRead(notificationId: string, userId: string) {
        return this.prisma.notification.updateMany({
            where: { id: BigInt(notificationId), userId },
            data: { isRead: true, readAt: new Date() },
        });
    }

    async markAllAsRead(userId: string) {
        return this.prisma.notification.updateMany({
            where: { userId, isRead: false },
            data: { isRead: true, readAt: new Date() },
        });
    }

    // Send notification to all devices of a user
    async sendToUser(
        userId: string,
        notification: {
            title: string;
            body: string;
            type: string;
            data?: Record<string, unknown>;
        },
    ) {
        // Get all FCM tokens for user
        const deviceTokens = await this.prisma.deviceToken.findMany({
            where: { userId },
            select: { fcmToken: true },
        });

        const tokens = deviceTokens.map((d) => d.fcmToken);

        // Store notification in DB
        await this.prisma.notification.create({
            data: {
                userId,
                title: notification.title,
                body: notification.body,
                type: notification.type,
                data: notification.data || {},
            },
        });

        // Send push notification
        if (tokens.length > 0) {
            const fcmData = notification.data
                ? Object.fromEntries(
                    Object.entries(notification.data).map(([k, v]) => [k, String(v)]),
                )
                : undefined;

            await this.fcmService.sendToMultipleDevices(
                tokens,
                { title: notification.title, body: notification.body },
                fcmData,
            );
        }
    }

    // Send notification to all users in a workspace
    async sendToWorkspace(
        workspaceId: string,
        notification: {
            title: string;
            body: string;
            type: string;
            data?: Record<string, unknown>;
        },
    ) {
        // Get all users in workspace
        const userWorkspaces = await this.prisma.userWorkspace.findMany({
            where: { workspaceId },
            select: { userId: true },
        });

        for (const uw of userWorkspaces) {
            await this.sendToUser(uw.userId, notification);
        }
    }

    // Alert notifications
    async notifyNodeOffline(nodeId: string, hostname: string, workspaceId: string) {
        await this.sendToWorkspace(workspaceId, {
            title: '🔴 Node Offline',
            body: `${hostname} has gone offline`,
            type: 'node_offline',
            data: {
                screen: 'NODE_DETAIL',
                node_id: nodeId,
            },
        });
    }

    async notifyNodeOnline(nodeId: string, hostname: string, workspaceId: string) {
        await this.sendToWorkspace(workspaceId, {
            title: '🟢 Node Online',
            body: `${hostname} is back online`,
            type: 'node_online',
            data: {
                screen: 'NODE_DETAIL',
                node_id: nodeId,
            },
        });
    }

    async notifyAlert(
        nodeId: string,
        hostname: string,
        severity: string,
        message: string,
        workspaceId: string,
    ) {
        const emoji = severity === 'CRITICAL' ? '🚨' : '⚠️';
        await this.sendToWorkspace(workspaceId, {
            title: `${emoji} ${severity} Alert`,
            body: `${hostname}: ${message}`,
            type: 'alert',
            data: {
                screen: 'NODE_DETAIL',
                node_id: nodeId,
                severity,
            },
        });
    }
}
