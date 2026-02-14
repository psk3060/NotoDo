export interface LoginRequest {
    userId: string;
    encryptedPassword?: string;
    encryptedAESKey?: string;
    iv?:string;
}

export interface LoginResponse {
    success: boolean;
    message?: string;
    data? : {
        userId : string;
        accessToken?:string;
    }
}

export interface AuthState {
    userId : string | null;
    isAuthenticated : boolean;
}

export interface AuthStore extends AuthState {
    setUserId : (userId : string) => void;
    setAuthenticated : (isAuthenticated : boolean) => void;
    clearAuth : () => void;
}

export interface AuthContextType {
    login : (userId:string, password:string) => Promise<LoginResponse>;
    logout : () => void;
}