import { type ReactNode, useState } from 'react';

import { AuthContext } from './AuthContext';

import localAuthStore from '../../store/authStore';

type Props = {
    children: ReactNode;
};

export default function AuthProvider({ children }: Props) {

    const authStore = localAuthStore();

    async function login(userId:string, password:string) {
        // TODO JWT Token 발급
        let isSuccess = (userId === 'demo' && password === 'dummy');

        if( isSuccess ) {
            authStore.setUserId(userId);

        }

        authStore.setAuthenticated(isSuccess);

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