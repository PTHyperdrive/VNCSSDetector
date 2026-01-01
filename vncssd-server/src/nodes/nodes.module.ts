import { Module, forwardRef } from '@nestjs/common';
import { JwtModule } from '@nestjs/jwt';
import { NodesController } from './nodes.controller';
import { NodesService } from './nodes.service';
import { NodesGateway } from './nodes.gateway';
import { EventsModule } from '../events/events.module';

@Module({
    imports: [
        JwtModule.register({}),
        forwardRef(() => EventsModule),
    ],
    controllers: [NodesController],
    providers: [NodesService, NodesGateway],
    exports: [NodesService, NodesGateway],
})
export class NodesModule { }
