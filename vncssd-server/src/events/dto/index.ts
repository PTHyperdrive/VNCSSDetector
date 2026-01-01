import { IsString, IsOptional, IsArray, IsEnum, IsDateString } from 'class-validator';
import { ApiPropertyOptional } from '@nestjs/swagger';

export enum SeverityFilter {
    LOW = 'LOW',
    MEDIUM = 'MEDIUM',
    HIGH = 'HIGH',
    CRITICAL = 'CRITICAL',
}

export class QueryEventsDto {
    @ApiPropertyOptional({ enum: SeverityFilter, isArray: true })
    @IsOptional()
    @IsArray()
    @IsEnum(SeverityFilter, { each: true })
    severity?: SeverityFilter[];

    @ApiPropertyOptional()
    @IsOptional()
    @IsString()
    nodeId?: string;

    @ApiPropertyOptional()
    @IsOptional()
    @IsDateString()
    from?: string;

    @ApiPropertyOptional()
    @IsOptional()
    @IsDateString()
    to?: string;

    @ApiPropertyOptional({ default: 1 })
    @IsOptional()
    page?: number = 1;

    @ApiPropertyOptional({ default: 50 })
    @IsOptional()
    limit?: number = 50;
}
