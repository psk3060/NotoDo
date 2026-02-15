import { type ReactNode } from 'react';

import { AuthContext } from './AuthContext';

import { toast } from "react-toastify";

import { LoginResponse } from '@/shared/types';
import localAuthStore from '@/features/auth/stores/authStore';

import * as authService from '@/features/auth/services/authService';

type Props = {
    children: ReactNode;
};

export default function AuthProvider({ children }: Props) {

    const authStore = localAuthStore();
    
    async function login(userId:string, password:string) : Promise<LoginResponse> {

        const response = await authService.login({userId, password});
        
        if(response.success) {
            authStore.setUserId(userId);
            // TODO 
            // authStore.setUserId(response.data.userId);
            
        }
        else {
            toast.error(response.message);
        }

        authStore.setAuthenticated(response.success);

        return response;
    }

    async function logout() {
        await authService.logout();
        authStore.clearAuth();
    }

    return (
        <AuthContext.Provider value={{ login, logout }}>
            {children}
        </AuthContext.Provider>
    );
}