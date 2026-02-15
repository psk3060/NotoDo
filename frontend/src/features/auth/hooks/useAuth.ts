import { useNavigate } from "react-router-dom";
import {authStore} from "@/features/auth/stores/authStore";
import { useCallback } from "react";
import { toast } from "react-toastify";
import { ROUTES, TOAST_MESSAGES } from "@/shared/constants";
import { LoginResponse } from "@/shared/types";

import * as authService from '@/features/auth/services/authService';

export function useAuth() {
    const navigate = useNavigate();
    const {userId, isAuthenticated, setUserId, setAuthenticated, clearAuth} = authStore();

    const login = useCallback(
        async (userId : string, password : string) : Promise<boolean> => {
            try {
                const response : LoginResponse = await authService.login({userId, password});

                if(response.success) {
                    setUserId(userId);
                    setAuthenticated(true);
                    return true;
                }
                else {
                    toast.error(response.message || TOAST_MESSAGES.AUTH.LOGIN_FAIL);
                    setAuthenticated(false);
                    return false;
                }
            }
            catch(error) {
                toast.error(TOAST_MESSAGES.AUTH.LOGIN_ERROR);
                setAuthenticated(false);
                return false;
            }
        },
        [setUserId, setAuthenticated]
    );
    
    const logout = useCallback(async () => {
            try {
                await authService.logout();
            }catch(error) {
                console.error("Logout error : ", error);
            } finally {
                clearAuth();
                navigate(ROUTES.LOGIN);
            }
        }
        , [clearAuth, navigate]
    );

    return {
        userId
        , isAuthenticated
        , login
        , logout
    };
    
}