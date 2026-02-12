import { type ReactNode } from 'react';

import { AuthContext } from './AuthContext';
import localAuthStore from '../../store/authStore';
import { loginService } from '../../service/LoginService';
import type LoginResponse from '../../model/LoginResponse';

type Props = {
    children: ReactNode;
};

export default function AuthProvider({ children }: Props) {

    const authStore = localAuthStore();

    async function login(userId:string, password:string) : Promise<LoginResponse> {

        const response = await loginService(userId, password);
        let result = response.data;

        if( response.data.success ) {
            authStore.setUserId(userId);
        }
        authStore.setAuthenticated(response.data.success);

        return result;
    }

    function logout() {
        authStore.clearAuth();
    }

    return (
        <AuthContext.Provider value={{ login, logout }}>
            {children}
        </AuthContext.Provider>
    );
}