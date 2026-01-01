import { IsString, IsOptional, IsBoolean } from 'class-validator';
import { ApiProperty, ApiPropertyOptional } from '@nestjs/swagger';

export class RegisterDeviceDto {
    @ApiProperty()
    @IsString()
    fcmToken: string;

    @ApiPropertyOptional()
    @IsOptional()
    @IsString()
    deviceInfo?: string;
}

export class QueryNotificationsDto {
    @ApiPropertyOptional()
    @IsOptional()
    @IsBoolean()
    isRead?: boolean;

    @ApiPropertyOptional({ default: 1 })
    @IsOptional()
    page?: number = 1;

    @ApiPropertyOptional({ default: 20 })
    @IsOptional()
    limit?: number = 20;
}
