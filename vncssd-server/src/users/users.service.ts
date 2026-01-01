import { Injectable } from '@nestjs/common';
import { PrismaService } from '../prisma';

@Injectable()
export class UsersService {
    constructor(private prisma: PrismaService) { }

    async findById(id: string) {
        return this.prisma.user.findUnique({
            where: { id },
            include: {
                workspaces: {
                    include: {
                        workspace: true,
                        role: true,
                    },
                },
            },
        });
    }

    async findByEmail(email: string) {
        return this.prisma.user.findUnique({
            where: { email: email.toLowerCase() },
        });
    }

    async getUserWorkspaces(userId: string) {
        return this.prisma.userWorkspace.findMany({
            where: { userId },
            include: {
                workspace: true,
                role: true,
            },
        });
    }

    async deactivateUser(userId: string) {
        return this.prisma.user.update({
            where: { id: userId },
            data: { isActive: false },
        });
    }

    async activateUser(userId: string) {
        return this.prisma.user.update({
            where: { id: userId },
            data: { isActive: true },
        });
    }
}
