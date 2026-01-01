import { Injectable } from '@nestjs/common';
import { PrismaService } from '../prisma';

@Injectable()
export class WorkspacesService {
    constructor(private prisma: PrismaService) { }

    async findById(id: string) {
        return this.prisma.workspace.findUnique({
            where: { id },
            include: {
                nodes: {
                    select: { id: true, status: true },
                },
                users: {
                    include: {
                        user: { select: { id: true, email: true, name: true } },
                        role: true,
                    },
                },
            },
        });
    }

    async getUserWorkspaces(userId: string) {
        const userWorkspaces = await this.prisma.userWorkspace.findMany({
            where: { userId },
            include: {
                workspace: true,
                role: true,
            },
        });

        return userWorkspaces.map((uw) => ({
            id: uw.workspace.id,
            name: uw.workspace.name,
            slug: uw.workspace.slug,
            role: uw.role.name,
        }));
    }

    async addUserToWorkspace(
        workspaceId: string,
        userId: string,
        roleId: number,
    ) {
        return this.prisma.userWorkspace.create({
            data: {
                userId,
                workspaceId,
                roleId,
            },
        });
    }

    async removeUserFromWorkspace(workspaceId: string, userId: string) {
        return this.prisma.userWorkspace.deleteMany({
            where: {
                userId,
                workspaceId,
            },
        });
    }
}
