import { type ReactNode } from 'react';

import { AuthContext } from './AuthContext';
import localAuthStore from '../../store/authStore';
import { loginProc, logoutProc } from '../../service/LoginService';
import type LoginResponse from '../../model/LoginResponse';
import { toast } from "react-toastify";

type Props = {
    children: ReactNode;
};

export default function AuthProvider({ children }: Props) {

    const authStore = localAuthStore();
    
    async function login(userId:string, password:string) : Promise<LoginResponse> {

        const response = await loginProc(userId, password);
        let result = response.data;

        if( response.data.success ) {
            authStore.setUserId(userId);
        }
        else {
            toast.error(response.data.message);
        }
        authStore.setAuthenticated(response.data.success);

        return result;
    }

    function logout() {
        logoutProc();
        authStore.clearAuth();
    }

    return (
        <AuthContext.Provider value={{ login, logout }}>
            {children}
        </AuthContext.Provider>
    );
}