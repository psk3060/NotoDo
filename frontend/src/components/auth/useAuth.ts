import { useContext } from "react";
import { AuthContext } from "./AuthContext";


export const useAuth = () => {
    const ctx = useContext(AuthContext);

    if (!ctx) {
        throw new Error("잘못된 접근입니다.");
    }
    
    return ctx;
}