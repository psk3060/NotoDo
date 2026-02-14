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