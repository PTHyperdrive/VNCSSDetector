import {
    Controller,
    Get,
    Post,
    Patch,
    Param,
    Query,
    Body,
    UseGuards,
} from '@nestjs/common';
import { ApiTags, ApiOperation, ApiBearerAuth } from '@nestjs/swagger';
import { AuthGuard } from '@nestjs/passport';
import { NotificationsService } from './notifications.service';
import { RegisterDeviceDto, QueryNotificationsDto } from './dto';
import { CurrentUser } from '../common/decorators';
import { successResponse, paginatedResponse } from '../common/response';

@ApiTags('Notifications')
@Controller()
@UseGuards(AuthGuard('jwt'))
@ApiBearerAuth()
export class NotificationsController {
    constructor(private notificationsService: NotificationsService) { }

    @Post('device-tokens')
    @ApiOperation({ summary: 'Register FCM device token' })
    async registerDevice(
        @Body() dto: RegisterDeviceDto,
        @CurrentUser() user: { id: string },
    ) {
        await this.notificationsService.registerDevice(
            user.id,
            dto.fcmToken,
            dto.deviceInfo,
        );
        return successResponse(null, 'Device registered');
    }

    @Get('notifications')
    @ApiOperation({ summary: 'Get notifications' })
    async findAll(
        @Query() query: QueryNotificationsDto,
        @CurrentUser() user: { id: string },
    ) {
        const result = await this.notificationsService.findAll(user.id, query);
        return {
            success: true,
            data: {
                notifications: result.notifications,
                unreadCount: result.unreadCount,
            },
            pagination: result.pagination,
        };
    }

    @Patch('notifications/:id/read')
    @ApiOperation({ summary: 'Mark notification as read' })
    async markAsRead(
        @Param('id') id: string,
        @CurrentUser() user: { id: string },
    ) {
        await this.notificationsService.markAsRead(id, user.id);
        return successResponse(null, 'Marked as read');
    }

    @Patch('notifications/read-all')
    @ApiOperation({ summary: 'Mark all notifications as read' })
    async markAllAsRead(@CurrentUser() user: { id: string }) {
        await this.notificationsService.markAllAsRead(user.id);
        return successResponse(null, 'All marked as read');
    }
}
