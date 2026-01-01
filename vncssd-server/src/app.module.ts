import { Module } from '@nestjs/common';
import { ConfigModule } from '@nestjs/config';
import { ThrottlerModule } from '@nestjs/throttler';
import { PrismaModule } from './prisma/prisma.module';
import { AuthModule } from './auth/auth.module';
import { UsersModule } from './users/users.module';
import { WorkspacesModule } from './workspaces/workspaces.module';
import { NodesModule } from './nodes/nodes.module';
import { EventsModule } from './events/events.module';
import { NotificationsModule } from './notifications/notifications.module';
import { StatusModule } from './status/status.module';
import { ApiKeysModule } from './api-keys/api-keys.module';
import { RealtimeModule } from './realtime/realtime.module';
import { AlertsModule } from './alerts/alerts.module';

@Module({
    imports: [
        // Config
        ConfigModule.forRoot({
            isGlobal: true,
            envFilePath: ['.env.local', '.env'],
        }),

        // Rate limiting
        ThrottlerModule.forRoot([
            {
                name: 'short',
                ttl: 1000,
                limit: 10,
            },
            {
                name: 'medium',
                ttl: 10000,
                limit: 50,
            },
            {
                name: 'long',
                ttl: 60000,
                limit: 100,
            },
        ]),

        // Database
        PrismaModule,

        // Feature modules
        AuthModule,
        UsersModule,
        WorkspacesModule,
        NodesModule,
        EventsModule,
        NotificationsModule,
        StatusModule,
        ApiKeysModule,
        RealtimeModule,
        AlertsModule,
    ],
})
export class AppModule { }


