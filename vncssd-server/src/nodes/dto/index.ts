import { IsString, IsOptional, IsArray, IsEnum } from 'class-validator';
import { ApiProperty, ApiPropertyOptional } from '@nestjs/swagger';

export enum NodeStatusFilter {
    ONLINE = 'ONLINE',
    OFFLINE = 'OFFLINE',
    DEGRADED = 'DEGRADED',
    PENDING = 'PENDING',
}

export class QueryNodesDto {
    @ApiPropertyOptional({ enum: NodeStatusFilter })
    @IsOptional()
    @IsEnum(NodeStatusFilter)
    status?: NodeStatusFilter;

    @ApiPropertyOptional()
    @IsOptional()
    @IsString()
    tag?: string;

    @ApiPropertyOptional({ default: 1 })
    @IsOptional()
    page?: number = 1;

    @ApiPropertyOptional({ default: 20 })
    @IsOptional()
    limit?: number = 20;
}

export class CreateCommandDto {
    @ApiProperty({ example: 'scan_path' })
    @IsString()
    commandType: string;

    @ApiPropertyOptional({ example: { path: '/var/log', recursive: true } })
    @IsOptional()
    params?: Record<string, unknown>;
}

export class ProvisionNodeDto {
    @ApiProperty({ example: 'ws-uuid' })
    @IsString()
    workspaceId: string;

    @ApiPropertyOptional({ example: ['production', 'dc-1'] })
    @IsOptional()
    @IsArray()
    @IsString({ each: true })
    tags?: string[];
}
