import {
    ExceptionFilter,
    Catch,
    ArgumentsHost,
    HttpException,
    HttpStatus,
} from '@nestjs/common';
import { Response } from 'express';
import { errorResponse } from '../response';

@Catch()
export class AllExceptionsFilter implements ExceptionFilter {
    catch(exception: unknown, host: ArgumentsHost) {
        const ctx = host.switchToHttp();
        const response = ctx.getResponse<Response>();

        let status = HttpStatus.INTERNAL_SERVER_ERROR;
        let code = 'INTERNAL_ERROR';
        let message = 'An unexpected error occurred';
        let details: unknown = undefined;

        if (exception instanceof HttpException) {
            status = exception.getStatus();
            const exceptionResponse = exception.getResponse();

            if (typeof exceptionResponse === 'string') {
                message = exceptionResponse;
            } else if (typeof exceptionResponse === 'object') {
                const resp = exceptionResponse as Record<string, unknown>;
                message = (resp.message as string) || message;
                code = (resp.error as string) || code;
                details = resp.details;
            }

            // Map common HTTP status to error codes
            switch (status) {
                case HttpStatus.UNAUTHORIZED:
                    code = 'UNAUTHORIZED';
                    break;
                case HttpStatus.FORBIDDEN:
                    code = 'FORBIDDEN';
                    break;
                case HttpStatus.NOT_FOUND:
                    code = 'NOT_FOUND';
                    break;
                case HttpStatus.BAD_REQUEST:
                    code = 'BAD_REQUEST';
                    break;
                case HttpStatus.CONFLICT:
                    code = 'CONFLICT';
                    break;
                case HttpStatus.TOO_MANY_REQUESTS:
                    code = 'RATE_LIMITED';
                    break;
            }
        } else if (exception instanceof Error) {
            message = exception.message;
            console.error('Unhandled exception:', exception);
        }

        response.status(status).json(errorResponse(code, message, details));
    }
}
