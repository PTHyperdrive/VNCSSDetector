import { Injectable, OnModuleInit } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import * as admin from 'firebase-admin';

@Injectable()
export class FcmService implements OnModuleInit {
    private firebaseApp: admin.app.App | null = null;

    constructor(private configService: ConfigService) { }

    async onModuleInit() {
        const projectId = this.configService.get('FCM_PROJECT_ID');
        const privateKeyPath = this.configService.get('FCM_PRIVATE_KEY_PATH');

        if (!projectId || !privateKeyPath) {
            console.warn('[FCM] Firebase not configured, push notifications disabled');
            return;
        }

        try {
            // eslint-disable-next-line @typescript-eslint/no-require-imports
            const serviceAccount = require(privateKeyPath);
            this.firebaseApp = admin.initializeApp({
                credential: admin.credential.cert(serviceAccount),
                projectId,
            });
            console.log('[FCM] Firebase initialized successfully');
        } catch (error) {
            console.warn('[FCM] Failed to initialize Firebase:', error);
        }
    }

    async sendToDevice(
        token: string,
        notification: { title: string; body: string },
        data?: Record<string, string>,
    ): Promise<boolean> {
        if (!this.firebaseApp) {
            console.warn('[FCM] Firebase not initialized, skipping push');
            return false;
        }

        try {
            await admin.messaging().send({
                token,
                notification,
                data,
                android: {
                    priority: 'high',
                    notification: {
                        channelId: 'alerts',
                    },
                },
            });
            return true;
        } catch (error) {
            console.error('[FCM] Failed to send push notification:', error);
            return false;
        }
    }

    async sendToMultipleDevices(
        tokens: string[],
        notification: { title: string; body: string },
        data?: Record<string, string>,
    ): Promise<{ successCount: number; failureCount: number }> {
        if (!this.firebaseApp || tokens.length === 0) {
            return { successCount: 0, failureCount: tokens.length };
        }

        try {
            const response = await admin.messaging().sendEachForMulticast({
                tokens,
                notification,
                data,
                android: {
                    priority: 'high',
                    notification: {
                        channelId: 'alerts',
                    },
                },
            });

            return {
                successCount: response.successCount,
                failureCount: response.failureCount,
            };
        } catch (error) {
            console.error('[FCM] Failed to send multicast push:', error);
            return { successCount: 0, failureCount: tokens.length };
        }
    }
}
