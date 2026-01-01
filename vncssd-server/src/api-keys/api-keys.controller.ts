import {
    Controller,
    Get,
    Post,
    Delete,
    Param,
    Body,
    UseGuards,
} from '@nestjs/common';
import { ApiTags, ApiOperation, ApiBearerAuth } from '@nestjs/swagger';
import { AuthGuard } from '@nestjs/passport';
import { ApiKeysService } from './api-keys.service';
import { CreateApiKeyDto } from './dto';
import { CurrentWorkspace, Roles } from '../common/decorators';
import { RolesGuard } from '../common/guards';
import { successResponse } from '../common/response';

@ApiTags('API Keys')
@Controller('api-keys')
@UseGuards(AuthGuard('jwt'), RolesGuard)
@ApiBearerAuth()
export class ApiKeysController {
    constructor(private apiKeysService: ApiKeysService) { }

    @Post()
    @Roles('admin')
    @ApiOperation({ summary: 'Generate new API key' })
    async create(
        @Body() dto: CreateApiKeyDto,
        @CurrentWorkspace() workspaceId: string,
    ) {
        const result = await this.apiKeysService.create(workspaceId, dto);
        return successResponse(result, 'API key created. Save the key now - it will not be shown again!');
    }

    @Get()
    @Roles('admin')
    @ApiOperation({ summary: 'List all API keys' })
    async findAll(@CurrentWorkspace() workspaceId: string) {
        const keys = await this.apiKeysService.findAll(workspaceId);
        return successResponse(keys);
    }

    @Delete(':id')
    @Roles('admin')
    @ApiOperation({ summary: 'Revoke/delete API key' })
    async delete(
        @Param('id') id: string,
        @CurrentWorkspace() workspaceId: string,
    ) {
        await this.apiKeysService.delete(id, workspaceId);
        return successResponse(null, 'API key deleted');
    }
}
