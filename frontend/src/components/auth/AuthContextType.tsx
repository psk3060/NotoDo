export interface AuthContextType {
    login : (userId:string, password:string) => Promise<boolean>;
    logout : () => void;
};