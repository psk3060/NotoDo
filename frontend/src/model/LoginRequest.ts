export default interface LoginRequest {
    userId: string;
    encryptedPassword?: string;
    encryptedAESKey?: string;
    iv?:string;
}