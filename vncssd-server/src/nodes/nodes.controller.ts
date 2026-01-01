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
import { NodesService } from './nodes.service';
import { NodesGateway } from './nodes.gateway';
import { QueryNodesDto, CreateCommandDto, ProvisionNodeDto } from './dto';
import { CurrentUser, Roles, RequirePermissions } from '../common/decorators';
import { RolesGuard, PermissionsGuard } from '../common/guards';
import { successResponse, paginatedResponse } from '../common/response';

@ApiTags('Nodes')
@Controller('nodes')
@UseGuards(AuthGuard('jwt'), RolesGuard, PermissionsGuard)
@ApiBearerAuth()
export class NodesController {
    constructor(
        private nodesService: NodesService,
        private nodesGateway: NodesGateway,
    ) { }

    @Get()
    @ApiOperation({ summary: 'List nodes in workspace' })
    async findAll(
        @Query() query: QueryNodesDto,
        @CurrentUser() user: { workspaceId: string },
    ) {
        const result = await this.nodesService.findAll(user.workspaceId, query);
        return paginatedResponse(
            result.nodes,
            result.pagination.page,
            result.pagination.limit,
            result.pagination.total,
        );
    }

    @Get('topology')
    @ApiOperation({ summary: 'Get nodes topology summary' })
    async getTopology(@CurrentUser() user: { workspaceId: string }) {
        const topology = await this.nodesService.getTopology(user.workspaceId);
        return successResponse(topology);
    }

    @Get(':id')
    @ApiOperation({ summary: 'Get node details' })
    async findOne(
        @Param('id') id: string,
        @CurrentUser() user: { workspaceId: string },
    ) {
        const node = await this.nodesService.findById(id, user.workspaceId);
        return successResponse({
            ...node,
            isOnline: this.nodesGateway.isNodeOnline(id),
        });
    }

    @Post(':id/commands')
    @Roles('admin', 'operator')
    @RequirePermissions('nodes.command')
    @ApiOperation({ summary: 'Send command to node' })
    async createCommand(
        @Param('id') id: string,
        @Body() dto: CreateCommandDto,
        @CurrentUser() user: { id: string; workspaceId: string },
    ) {
        const command = await this.nodesService.createCommand(
            id,
            user.workspaceId,
            user.id,
            dto,
        );

        // Send command via WebSocket if node is connected
        await this.nodesGateway.sendCommand(id, {
            command_id: command.commandId,
            command_type: dto.commandType,
            params: dto.params,
            timeout_seconds: 300,
        });

        return successResponse(command, 'Command sent');
    }

    @Post('provision')
    @Roles('admin')
    @ApiOperation({ summary: 'Provision a new node' })
    async provision(
        @Body() dto: ProvisionNodeDto,
        @CurrentUser() user: { workspaceId: string },
    ) {
        const result = await this.nodesService.provisionNode(
            dto.workspaceId || user.workspaceId,
            dto.tags,
        );
        return successResponse(result, 'Node provisioned');
    }

    @Patch(':id/location')
    @Roles('admin', 'operator')
    @ApiOperation({ summary: 'Update node location for map' })
    async updateLocation(
        @Param('id') id: string,
        @Body() dto: { latitude?: number; longitude?: number; locationName?: string },
        @CurrentUser() user: { workspaceId: string },
    ) {
        const node = await this.nodesService.updateLocation(
            id,
            user.workspaceId,
            dto,
        );
        return successResponse(node, 'Location updated');
    }
}
