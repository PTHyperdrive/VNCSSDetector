import { Module, Global } from '@nestjs/common';
import { ClientGateway } from './client.gateway';

@Global()
@Module({
    providers: [ClientGateway],
    exports: [ClientGateway],
})
export class RealtimeModule { }
