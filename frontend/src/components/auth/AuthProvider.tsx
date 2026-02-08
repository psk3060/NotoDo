import { type ReactNode } from 'react';

import { AuthContext } from './AuthContext';

import localAuthStore from '../../store/authStore';

import { loginService } from '../../service/LoginService';

type Props = {
    children: ReactNode;
};

export default function AuthProvider({ children }: Props) {

    const authStore = localAuthStore();

    async function login(userId:string, password:string) : Promise<boolean> {

        let isSuccess = false;

        try {
            const response = await loginService(userId, password);
            isSuccess = response.data;
        }
        catch (e) {
            isSuccess = false;
        }
        finally {
            authStore.setAuthenticated(isSuccess);
            if( isSuccess ) {
                authStore.setUserId(userId);
            }
        }

        return isSuccess;
    }

    function logout() {
        authStore.setAuthenticated(false);
        authStore.setUserId("");
    }

    return (
        <AuthContext.Provider value={{ login, logout }}>
            {children}
        </AuthContext.Provider>
    );
}