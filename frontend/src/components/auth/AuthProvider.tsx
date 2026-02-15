import { type ReactNode } from 'react';

import { AuthContext } from './AuthContext';

import { toast } from "react-toastify";

import { LoginResponse } from '@/shared/types';

import * as authService from '@/features/auth/services/authService';
import { authStore } from '@/features/auth/stores/authStore';

type Props = {
    children: ReactNode;
};

export default function AuthProvider({ children }: Props) {

    const {setUserId, setAuthenticated, clearAuth} = authStore();

    async function login(userId:string, password:string) : Promise<LoginResponse> {

        const response = await authService.login({userId, password});
        
        if(response.success) {
            setUserId(userId);
            // TODO 
            // authStore().setUserId(response.data.userId);
            
        }
        else {
            toast.error(response.message);
        }

        setAuthenticated(response.success);

        return response;
    }

    async function logout() {
        await authService.logout();
        clearAuth();
    }

    return (
        <AuthContext.Provider value={{ login, logout }}>
            {children}
        </AuthContext.Provider>
    );
}