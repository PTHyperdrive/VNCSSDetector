import { Controller, Get, Post, Body, Query, UseGuards } from '@nestjs/common';
import { ApiTags, ApiOperation, ApiBearerAuth } from '@nestjs/swagger';
import { AuthGuard } from '@nestjs/passport';
import { AlertsService } from './alerts.service';
import { CurrentUser } from '../common/decorators';
import { successResponse } from '../common/response';

@ApiTags('Alerts')
@Controller('alerts')
@UseGuards(AuthGuard('jwt'))
@ApiBearerAuth()
export class AlertsController {
    constructor(private alertsService: AlertsService) { }

    @Get('active')
    @ApiOperation({ summary: 'Get active threats' })
    async getActiveThreats() {
        const threats = this.alertsService.getActiveThreats();
        return successResponse(threats);
    }

    @Post('check-proximity')
    @ApiOperation({ summary: 'Check if client is near any active threat' })
    async checkProximity(
        @Body() dto: { latitude: number; longitude: number; radiusKm?: number },
    ) {
        const result = await this.alertsService.checkClientProximity(
            dto.latitude,
            dto.longitude,
            dto.radiusKm,
        );
        return successResponse(result);
    }
}
