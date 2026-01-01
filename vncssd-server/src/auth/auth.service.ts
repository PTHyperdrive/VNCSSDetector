import {
    Injectable,
    ConflictException,
    UnauthorizedException,
    BadRequestException,
} from '@nestjs/common';
import { JwtService } from '@nestjs/jwt';
import { ConfigService } from '@nestjs/config';
import * as bcrypt from 'bcrypt';
import { v4 as uuidv4 } from 'uuid';
import { PrismaService } from '../prisma';
import { RegisterDto, LoginDto, AuthResponse, TokensResponse } from './dto';
import { JwtPayload } from './strategies/jwt.strategy';

@Injectable()
export class AuthService {
    constructor(
        private prisma: PrismaService,
        private jwtService: JwtService,
        private configService: ConfigService,
    ) { }

    async register(dto: RegisterDto): Promise<AuthResponse> {
        // Check if user exists
        const existingUser = await this.prisma.user.findUnique({
            where: { email: dto.email.toLowerCase() },
        });

        if (existingUser) {
            throw new ConflictException('Email already registered');
        }

        // Hash password
        const passwordHash = await bcrypt.hash(dto.password, 12);

        // Create user with a default workspace
        const user = await this.prisma.$transaction(async (tx) => {
            // Create user
            const newUser = await tx.user.create({
                data: {
                    email: dto.email.toLowerCase(),
                    passwordHash,
                    name: dto.name,
                },
            });

            // Create default workspace
            const workspace = await tx.workspace.create({
                data: {
                    name: `${dto.name}'s Workspace`,
                    slug: `ws-${uuidv4().substring(0, 8)}`,
                },
            });

            // Get admin role
            let adminRole = await tx.role.findUnique({ where: { name: 'admin' } });
            if (!adminRole) {
                adminRole = await tx.role.create({
                    data: { name: 'admin', permissions: { all: true } },
                });
            }

            // Link user to workspace as admin
            await tx.userWorkspace.create({
                data: {
                    userId: newUser.id,
                    workspaceId: workspace.id,
                    roleId: adminRole.id,
                },
            });

            return newUser;
        });

        // Generate tokens
        const tokens = await this.generateTokens(user.id, user.email);

        return {
            user: {
                id: user.id,
                email: user.email,
                name: user.name,
            },
            tokens,
        };
    }

    async login(dto: LoginDto): Promise<AuthResponse> {
        const user = await this.prisma.user.findUnique({
            where: { email: dto.email.toLowerCase() },
            include: {
                workspaces: {
                    include: {
                        workspace: true,
                        role: true,
                    },
                },
            },
        });

        if (!user) {
            throw new UnauthorizedException('Invalid credentials');
        }

        if (!user.isActive) {
            throw new UnauthorizedException('Account is deactivated');
        }

        const isPasswordValid = await bcrypt.compare(dto.password, user.passwordHash);
        if (!isPasswordValid) {
            throw new UnauthorizedException('Invalid credentials');
        }

        // Generate tokens
        const tokens = await this.generateTokens(user.id, user.email);

        return {
            user: {
                id: user.id,
                email: user.email,
                name: user.name,
                workspaces: user.workspaces.map((uw) => ({
                    id: uw.workspace.id,
                    name: uw.workspace.name,
                    role: uw.role.name,
                })),
            },
            tokens,
        };
    }

    async refreshTokens(refreshToken: string): Promise<TokensResponse> {
        try {
            const payload = this.jwtService.verify<JwtPayload>(refreshToken, {
                secret: this.configService.get('JWT_REFRESH_SECRET'),
            });

            if (payload.type !== 'refresh') {
                throw new BadRequestException('Invalid token type');
            }

            // Check if refresh token exists in DB
            const storedToken = await this.prisma.refreshToken.findUnique({
                where: { token: refreshToken },
                include: { user: true },
            });

            if (!storedToken || storedToken.expiresAt < new Date()) {
                throw new UnauthorizedException('Invalid or expired refresh token');
            }

            // Delete old refresh token
            await this.prisma.refreshToken.delete({ where: { id: storedToken.id } });

            // Generate new tokens
            return this.generateTokens(storedToken.user.id, storedToken.user.email);
        } catch (error) {
            if (error instanceof UnauthorizedException || error instanceof BadRequestException) {
                throw error;
            }
            throw new UnauthorizedException('Invalid refresh token');
        }
    }

    async logout(userId: string): Promise<void> {
        // Delete all refresh tokens for user
        await this.prisma.refreshToken.deleteMany({
            where: { userId },
        });
    }

    private async generateTokens(userId: string, email: string): Promise<TokensResponse> {
        const accessPayload: JwtPayload = {
            sub: userId,
            email,
            type: 'access',
        };

        const refreshPayload: JwtPayload = {
            sub: userId,
            email,
            type: 'refresh',
        };

        const accessExpiresIn = this.configService.get('JWT_ACCESS_EXPIRES_IN', '15m');
        const refreshExpiresIn = this.configService.get('JWT_REFRESH_EXPIRES_IN', '7d');

        const [accessToken, refreshToken] = await Promise.all([
            this.jwtService.signAsync(accessPayload, {
                secret: this.configService.get('JWT_ACCESS_SECRET'),
                expiresIn: accessExpiresIn,
            }),
            this.jwtService.signAsync(refreshPayload, {
                secret: this.configService.get('JWT_REFRESH_SECRET'),
                expiresIn: refreshExpiresIn,
            }),
        ]);

        // Store refresh token in DB
        const expiresAt = new Date();
        expiresAt.setDate(expiresAt.getDate() + 7); // 7 days

        await this.prisma.refreshToken.create({
            data: {
                userId,
                token: refreshToken,
                expiresAt,
            },
        });

        return {
            accessToken,
            refreshToken,
            expiresIn: 900, // 15 minutes in seconds
        };
    }
}
