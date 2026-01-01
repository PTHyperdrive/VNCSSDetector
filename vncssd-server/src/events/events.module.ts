import { Module, forwardRef } from '@nestjs/common';
import { EventsController } from './events.controller';
import { EventsService } from './events.service';
import { NodesModule } from '../nodes/nodes.module';

@Module({
    imports: [forwardRef(() => NodesModule)],
    controllers: [EventsController],
    providers: [EventsService],
    exports: [EventsService],
})
export class EventsModule { }
