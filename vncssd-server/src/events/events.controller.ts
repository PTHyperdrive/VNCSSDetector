import { Controller, Get, Query, UseGuards } from '@nestjs/common';
import { ApiTags, ApiOperation, ApiBearerAuth } from '@nestjs/swagger';
import { AuthGuard } from '@nestjs/passport';
import { EventsService } from './events.service';
import { QueryEventsDto } from './dto';
import { CurrentUser } from '../common/decorators';
import { paginatedResponse } from '../common/response';

@ApiTags('Events')
@Controller('events')
@UseGuards(AuthGuard('jwt'))
@ApiBearerAuth()
export class EventsController {
    constructor(private eventsService: EventsService) { }

    @Get()
    @ApiOperation({ summary: 'List events with filters' })
    async findAll(
        @Query() query: QueryEventsDto,
        @CurrentUser() user: { workspaceId: string },
    ) {
        const result = await this.eventsService.findAll(user.workspaceId, query);
        return paginatedResponse(
            result.events,
            result.pagination.page,
            result.pagination.limit,
            result.pagination.total,
        );
    }
}
