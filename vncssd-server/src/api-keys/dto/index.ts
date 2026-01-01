import { IsString, IsOptional, IsDateString, IsObject } from 'class-validator';
import { ApiProperty, ApiPropertyOptional } from '@nestjs/swagger';

export class CreateApiKeyDto {
    @ApiProperty({ description: 'Name for this API key' })
    @IsString()
    name: string;

    @ApiPropertyOptional({ description: 'Custom permissions' })
    @IsOptional()
    @IsObject()
    permissions?: Record<string, boolean>;

    @ApiPropertyOptional({ description: 'Expiration date' })
    @IsOptional()
    @IsDateString()
    expiresAt?: string;
}

export class ApiKeyResponseDto {
    id: string;
    name: string;
    prefix: string;
    permissions: Record<string, boolean>;
    isActive: boolean;
    lastUsedAt: Date | null;
    expiresAt: Date | null;
    createdAt: Date;
}

export class GeneratedApiKeyDto extends ApiKeyResponseDto {
    // Only returned once when key is created
    key: string;
}
