import { Injectable, NotFoundException } from '@nestjs/common';
import { PrismaService } from '../prisma';
import { CreateApiKeyDto, ApiKeyResponseDto, GeneratedApiKeyDto } from './dto';
import * as crypto from 'crypto';

@Injectable()
export class ApiKeysService {
    constructor(private prisma: PrismaService) { }

    /**
     * Generate a new API key for a workspace
     */
    async create(workspaceId: string, dto: CreateApiKeyDto): Promise<GeneratedApiKeyDto> {
        // Generate a secure random key
        const rawKey = `vnc_${crypto.randomBytes(32).toString('hex')}`;
        const prefix = rawKey.substring(0, 12) + '...';
        const keyHash = crypto.createHash('sha256').update(rawKey).digest('hex');

        const apiKey = await this.prisma.apiKey.create({
            data: {
                workspaceId,
                name: dto.name,
                keyHash,
                prefix,
                permissions: dto.permissions || {},
                expiresAt: dto.expiresAt ? new Date(dto.expiresAt) : null,
            },
        });

        return {
            id: apiKey.id,
            name: apiKey.name,
            prefix: apiKey.prefix,
            permissions: apiKey.permissions as Record<string, boolean>,
            isActive: apiKey.isActive,
            lastUsedAt: apiKey.lastUsedAt,
            expiresAt: apiKey.expiresAt,
            createdAt: apiKey.createdAt,
            key: rawKey, // Only returned once!
        };
    }

    /**
     * List all API keys for a workspace
     */
    async findAll(workspaceId: string): Promise<ApiKeyResponseDto[]> {
        const keys = await this.prisma.apiKey.findMany({
            where: { workspaceId },
            orderBy: { createdAt: 'desc' },
        });

        return keys.map((key) => ({
            id: key.id,
            name: key.name,
            prefix: key.prefix,
            permissions: key.permissions as Record<string, boolean>,
            isActive: key.isActive,
            lastUsedAt: key.lastUsedAt,
            expiresAt: key.expiresAt,
            createdAt: key.createdAt,
        }));
    }

    /**
     * Revoke an API key
     */
    async revoke(keyId: string, workspaceId: string): Promise<void> {
        const key = await this.prisma.apiKey.findFirst({
            where: { id: keyId, workspaceId },
        });

        if (!key) {
            throw new NotFoundException('API key not found');
        }

        await this.prisma.apiKey.update({
            where: { id: keyId },
            data: { isActive: false },
        });
    }

    /**
     * Delete an API key
     */
    async delete(keyId: string, workspaceId: string): Promise<void> {
        const key = await this.prisma.apiKey.findFirst({
            where: { id: keyId, workspaceId },
        });

        if (!key) {
            throw new NotFoundException('API key not found');
        }

        await this.prisma.apiKey.delete({ where: { id: keyId } });
    }

    /**
     * Validate an API key and return workspace ID if valid
     */
    async validateKey(rawKey: string): Promise<{ workspaceId: string; permissions: Record<string, boolean> } | null> {
        const keyHash = crypto.createHash('sha256').update(rawKey).digest('hex');

        const apiKey = await this.prisma.apiKey.findUnique({
            where: { keyHash },
        });

        if (!apiKey) return null;
        if (!apiKey.isActive) return null;
        if (apiKey.expiresAt && apiKey.expiresAt < new Date()) return null;

        // Update last used
        await this.prisma.apiKey.update({
            where: { id: apiKey.id },
            data: { lastUsedAt: new Date() },
        });

        return {
            workspaceId: apiKey.workspaceId,
            permissions: apiKey.permissions as Record<string, boolean>,
        };
    }
}
