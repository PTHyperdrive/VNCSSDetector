export interface ApiResponse<T = unknown> {
    success: boolean;
    data?: T;
    message?: string;
    error?: {
        code: string;
        message: string;
        details?: unknown;
    };
}

export interface PaginatedResponse<T> extends ApiResponse<T> {
    pagination: {
        page: number;
        limit: number;
        total: number;
        totalPages: number;
    };
}

export function successResponse<T>(data: T, message?: string): ApiResponse<T> {
    return {
        success: true,
        data,
        message,
    };
}

export function errorResponse(code: string, message: string, details?: unknown): ApiResponse {
    return {
        success: false,
        error: {
            code,
            message,
            details,
        },
    };
}

export function paginatedResponse<T>(
    data: T,
    page: number,
    limit: number,
    total: number,
): PaginatedResponse<T> {
    return {
        success: true,
        data,
        pagination: {
            page,
            limit,
            total,
            totalPages: Math.ceil(total / limit),
        },
    };
}
