import type LoginResponse from "../../model/LoginResponse";

export interface AuthContextType {
    login : (userId:string, password:string) => Promise<LoginResponse>;
    logout : () => void;
};