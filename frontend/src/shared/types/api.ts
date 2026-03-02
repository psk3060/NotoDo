export interface ApiError {
    code : string;
    message : string;
    status? : number;
}

export interface ApiResponse<T> {
    data : T;
    success : boolean;
    message? : string;
}

export interface HttpApiError {
    response?: {
        data?: {
            code?: string;
            message?: string;
        };
    };
}

export interface PagedResponse<T> {
    data: T[];
    total: number;  // 전체 개수
    message? : string;
    totalPages : number;
}

export interface SearchParam {
    title: string,
    status: string,
    priority: string,
}