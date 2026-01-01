import { Injectable, NotFoundException } from '@nestjs/common';
import { PrismaService } from '../prisma';
import { NodeStatus, Prisma } from '@prisma/client';
import { QueryNodesDto, CreateCommandDto } from './dto';
import { v4 as uuidv4 } from 'uuid';

@Injectable()
export class NodesService {
    constructor(private prisma: PrismaService) { }

    async findAll(workspaceId: string, query: QueryNodesDto) {
        const { status, tag, page = 1, limit = 20 } = query;
        const skip = (page - 1) * limit;

        const where: Prisma.NodeWhereInput = {
            workspaceId,
            ...(status && { status: status as NodeStatus }),
            ...(tag && { tags: { has: tag } }),
        };

        const [nodes, total] = await Promise.all([
            this.prisma.node.findMany({
                where,
                skip,
                take: limit,
                orderBy: { lastSeen: 'desc' },
                include: {
                    metrics: {
                        take: 1,
                        orderBy: { recordedAt: 'desc' },
                    },
                },
            }),
            this.prisma.node.count({ where }),
        ]);

        return {
            nodes: nodes.map((node) => ({
                id: node.id,
                hostname: node.hostname,
                ipAddress: node.ipAddress,
                status: node.status,
                tags: node.tags,
                lastSeen: node.lastSeen,
                detectorStatus: (node.metadata as Record<string, unknown>)?.detectorStatus,
                cpuUsage: node.metrics[0]?.metrics
                    ? (node.metrics[0].metrics as Record<string, number>).cpu_usage
                    : null,
                memoryUsage: node.metrics[0]?.metrics
                    ? (node.metrics[0].metrics as Record<string, number>).memory_usage
                    : null,
            })),
            pagination: {
                page,
                limit,
                total,
                totalPages: Math.ceil(total / limit),
            },
        };
    }

    async findById(id: string, workspaceId: string) {
        const node = await this.prisma.node.findFirst({
            where: { id, workspaceId },
            include: {
                metrics: {
                    take: 1,
                    orderBy: { recordedAt: 'desc' },
                },
            },
        });

        if (!node) {
            throw new NotFoundException('Node not found');
        }

        return {
            id: node.id,
            nodeKey: node.nodeKey.substring(0, 8) + '***',
            hostname: node.hostname,
            ipAddress: node.ipAddress,
            os: node.os,
            version: node.version,
            status: node.status,
            tags: node.tags,
            capabilities: node.capabilities,
            lastSeen: node.lastSeen,
            registeredAt: node.registeredAt,
            metadata: node.metadata,
            currentMetrics: node.metrics[0]?.metrics || null,
        };
    }

    async getTopology(workspaceId: string) {
        const nodes = await this.prisma.node.findMany({
            where: { workspaceId },
            select: { status: true, tags: true },
        });

        const summary = {
            total: nodes.length,
            online: nodes.filter((n) => n.status === 'ONLINE').length,
            offline: nodes.filter((n) => n.status === 'OFFLINE').length,
            degraded: nodes.filter((n) => n.status === 'DEGRADED').length,
        };

        // Group by tags
        const tagMap = new Map<string, { total: number; online: number }>();
        nodes.forEach((node) => {
            node.tags.forEach((tag) => {
                const existing = tagMap.get(tag) || { total: 0, online: 0 };
                existing.total++;
                if (node.status === 'ONLINE') existing.online++;
                tagMap.set(tag, existing);
            });
        });

        const byTag = Array.from(tagMap.entries()).map(([tag, stats]) => ({
            tag,
            ...stats,
        }));

        return { summary, byTag };
    }

    async createCommand(
        nodeId: string,
        workspaceId: string,
        userId: string,
        dto: CreateCommandDto,
    ) {
        // Verify node belongs to workspace
        const node = await this.prisma.node.findFirst({
            where: { id: nodeId, workspaceId },
        });

        if (!node) {
            throw new NotFoundException('Node not found');
        }

        const command = await this.prisma.command.create({
            data: {
                nodeId,
                issuedById: userId,
                commandType: dto.commandType,
                payload: dto.params || {},
                expiresAt: new Date(Date.now() + 5 * 60 * 1000), // 5 minutes
            },
        });

        return {
            commandId: command.id,
            status: command.status,
            issuedAt: command.issuedAt,
        };
    }

    async provisionNode(workspaceId: string, tags: string[] = []) {
        const nodeKey = `node-${uuidv4()}`;

        const node = await this.prisma.node.create({
            data: {
                nodeKey,
                workspaceId,
                hostname: 'pending',
                status: 'PENDING',
                tags,
            },
        });

        return {
            nodeId: node.id,
            nodeKey,
            message: 'Node provisioned. Use this key to connect the detector.',
        };
    }

    // Called by WebSocket gateway when node registers
    async registerNode(
        nodeKey: string,
        data: {
            hostname: string;
            ipAddress?: string;
            os?: string;
            version?: string;
            capabilities?: string[];
            metadata?: Record<string, unknown>;
        },
    ) {
        return this.prisma.node.update({
            where: { nodeKey },
            data: {
                hostname: data.hostname,
                ipAddress: data.ipAddress,
                os: data.os,
                version: data.version,
                capabilities: data.capabilities || [],
                metadata: data.metadata || {},
                status: 'ONLINE',
                lastSeen: new Date(),
            },
        });
    }

    // Called by WebSocket gateway on heartbeat
    async updateHeartbeat(nodeId: string, metrics?: Record<string, unknown>) {
        const updates: Prisma.NodeUpdateInput = {
            lastSeen: new Date(),
            status: 'ONLINE',
        };

        await this.prisma.node.update({
            where: { id: nodeId },
            data: updates,
        });

        if (metrics) {
            await this.prisma.nodeMetric.create({
                data: {
                    nodeId,
                    metrics,
                },
            });
        }
    }

    // Called by WebSocket gateway when node disconnects
    async markOffline(nodeId: string) {
        return this.prisma.node.update({
            where: { id: nodeId },
            data: { status: 'OFFLINE' },
        });
    }

    async getNodeByKey(nodeKey: string) {
        return this.prisma.node.findUnique({
            where: { nodeKey },
        });
    }

    // Update node location for map display
    async updateLocation(
        nodeId: string,
        workspaceId: string,
        data: { latitude?: number; longitude?: number; locationName?: string },
    ) {
        const node = await this.prisma.node.findFirst({
            where: { id: nodeId, workspaceId },
        });

        if (!node) {
            throw new NotFoundException('Node not found');
        }

        return this.prisma.node.update({
            where: { id: nodeId },
            data: {
                latitude: data.latitude,
                longitude: data.longitude,
                locationName: data.locationName,
            },
            select: {
                id: true,
                hostname: true,
                latitude: true,
                longitude: true,
                locationName: true,
            },
        });
    }
}

