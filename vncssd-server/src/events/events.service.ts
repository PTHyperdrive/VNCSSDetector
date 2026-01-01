import { Injectable } from '@nestjs/common';
import { PrismaService } from '../prisma';
import { EventSeverity, Prisma, CommandStatus } from '@prisma/client';
import { QueryEventsDto } from './dto';

@Injectable()
export class EventsService {
    constructor(private prisma: PrismaService) { }

    async findAll(workspaceId: string, query: QueryEventsDto) {
        const { severity, nodeId, from, to, page = 1, limit = 50 } = query;
        const skip = (page - 1) * limit;

        // Get node IDs in workspace
        const workspaceNodes = await this.prisma.node.findMany({
            where: { workspaceId },
            select: { id: true },
        });
        const nodeIds = workspaceNodes.map((n) => n.id);

        const where: Prisma.NodeEventWhereInput = {
            nodeId: nodeId ? nodeId : { in: nodeIds },
            ...(severity && { severity: { in: severity as EventSeverity[] } }),
            ...(from && { occurredAt: { gte: new Date(from) } }),
            ...(to && { occurredAt: { lte: new Date(to) } }),
        };

        const [events, total] = await Promise.all([
            this.prisma.nodeEvent.findMany({
                where,
                skip,
                take: limit,
                orderBy: { occurredAt: 'desc' },
                include: {
                    node: {
                        select: { id: true, hostname: true },
                    },
                },
            }),
            this.prisma.nodeEvent.count({ where }),
        ]);

        return {
            events: events.map((e) => ({
                id: e.id.toString(),
                nodeId: e.nodeId,
                nodeHostname: e.node.hostname,
                eventType: e.eventType,
                severity: e.severity,
                message: e.message,
                data: e.data,
                occurredAt: e.occurredAt,
            })),
            pagination: {
                page,
                limit,
                total,
                totalPages: Math.ceil(total / limit),
            },
        };
    }

    async createEvent(
        nodeId: string,
        data: {
            eventType: string;
            severity: string;
            message: string;
            data?: Record<string, unknown>;
        },
    ) {
        const event = await this.prisma.nodeEvent.create({
            data: {
                nodeId,
                eventType: data.eventType,
                severity: data.severity.toUpperCase() as EventSeverity,
                message: data.message,
                data: data.data || {},
            },
            include: {
                node: {
                    select: { workspaceId: true, hostname: true },
                },
            },
        });

        // TODO: Trigger notifications if severity is HIGH or CRITICAL
        if (
            event.severity === 'HIGH' ||
            event.severity === 'CRITICAL'
        ) {
            // This will be handled by NotificationsService
            console.log(`[ALERT] High severity event from ${event.node.hostname}: ${event.message}`);
        }

        return event;
    }

    async updateCommandStatus(commandId: string, status: string) {
        return this.prisma.command.update({
            where: { id: commandId },
            data: { status: status.toUpperCase() as CommandStatus },
        });
    }

    async saveCommandResult(
        commandId: string,
        status: string,
        result: Record<string, unknown>,
    ) {
        await this.prisma.$transaction([
            this.prisma.command.update({
                where: { id: commandId },
                data: { status: status.toUpperCase() as CommandStatus },
            }),
            this.prisma.commandResult.create({
                data: {
                    commandId,
                    status,
                    result,
                },
            }),
        ]);
    }
}
