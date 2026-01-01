import { Injectable, UnauthorizedException } from '@nestjs/common';
import { PassportStrategy } from '@nestjs/passport';
import { ExtractJwt, Strategy } from 'passport-jwt';
import { ConfigService } from '@nestjs/config';
import { PrismaService } from '../../prisma';

export interface JwtPayload {
    sub: string;
    email: string;
    workspaceId?: string;
    role?: string;
    permissions?: Record<string, boolean>;
    type: 'access' | 'refresh';
}

@Injectable()
export class JwtStrategy extends PassportStrategy(Strategy, 'jwt') {
    constructor(
        private configService: ConfigService,
        private prisma: PrismaService,
    ) {
        super({
            jwtFromRequest: ExtractJwt.fromAuthHeaderAsBearerToken(),
            ignoreExpiration: false,
            secretOrKey: configService.get<string>('JWT_ACCESS_SECRET'),
        });
    }

    async validate(payload: JwtPayload) {
        if (payload.type !== 'access') {
            throw new UnauthorizedException('Invalid token type');
        }

        const user = await this.prisma.user.findUnique({
            where: { id: payload.sub },
            include: {
                workspaces: {
                    include: {
                        workspace: true,
                        role: true,
                    },
                },
            },
        });

        if (!user || !user.isActive) {
            throw new UnauthorizedException('User not found or inactive');
        }

        // Get the first workspace for convenience (can be overridden by header)
        const primaryWorkspace = user.workspaces[0];

        return {
            id: user.id,
            email: user.email,
            name: user.name,
            workspaceId: primaryWorkspace?.workspace.id,
            role: primaryWorkspace?.role.name,
            permissions: primaryWorkspace?.role.permissions as Record<string, boolean>,
        };
    }
}
