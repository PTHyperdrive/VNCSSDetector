import { Controller, Get } from '@nestjs/common';
import { ApiTags, ApiOperation } from '@nestjs/swagger';
import { ConfigService } from '@nestjs/config';
import { PrismaService } from '../prisma';
import { Public } from '../common/decorators';
import { successResponse } from '../common/response';

@ApiTags('Status')
@Controller('status')
export class StatusController {
    private startTime = Date.now();

    constructor(
        private configService: ConfigService,
        private prisma: PrismaService,
    ) { }

    @Public()
    @Get()
    @ApiOperation({ summary: 'Get server status' })
    async getStatus() {
        let dbStatus = 'disconnected';
        let nodesOnline = 0;
        let nodesTotal = 0;

        try {
            await this.prisma.$queryRaw`SELECT 1`;
            dbStatus = 'connected';

            const [online, total] = await Promise.all([
                this.prisma.node.count({ where: { status: 'ONLINE' } }),
                this.prisma.node.count(),
            ]);
            nodesOnline = online;
            nodesTotal = total;
        } catch (error) {
            dbStatus = 'error';
        }

        const uptimeSeconds = Math.floor((Date.now() - this.startTime) / 1000);
        const isHealthy = dbStatus === 'connected';

        return successResponse({
            status: isHealthy ? 'healthy' : 'degraded',
            version: this.configService.get('SERVER_VERSION', '1.0.0'),
            uptimeSeconds,
            database: dbStatus,
            redis: 'connected', // TODO: actual Redis health check
            nodesOnline,
            nodesTotal,
        });
    }

    @Get('health')
    @Public()
    @ApiOperation({ summary: 'Health check endpoint' })
    async healthCheck() {
        try {
            await this.prisma.$queryRaw`SELECT 1`;
            return { status: 'ok' };
        } catch {
            return { status: 'error' };
        }
    }
}
