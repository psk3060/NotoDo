import { useAuth } from '@/features/auth/hooks/useAuth';
import { useCallback } from "react";
import { HttpApiError } from '../types/api';
import {API_ENDPOINTS, ERROR_CODES, TOAST_MESSAGES} from '@/shared/constants';
import { toast } from "react-toastify";
import { apiClient } from "@/config/apiClient";


/**
 * API 호출 시 토큰 검증 및 갱신을 처리하는 커스텀 훅
 */
export function useApiWithAuth() {
    const {logout} = useAuth();


    /**
     * API 함수를 실행하면서 토큰 에러를 자동으로 처리(로그인 혹은 RTR)
     */
    const executeWithAuth = useCallback(
        async <T>(apiCall: () => Promise<T>): Promise<T | undefined> => {
            try {
                return await apiCall();
            } catch(error) {
                const apiError = error as HttpApiError;
                const errorCode = apiError.response?.data?.code;

                switch(errorCode) {
                    case ERROR_CODES.AUTH.TOKEN_EXPIRED:
                        // Access Token 만료 시 갱신 시도
                        try {
                            await apiClient.post(API_ENDPOINTS.AUTH.REFRESH);

                            return await apiCall();
                        }
                        catch(refreshError) {
                            toast.error(TOAST_MESSAGES.AUTH.LOGIN_REQUIRED);
                            await logout();
                            return undefined;

                        }
                    case ERROR_CODES.AUTH.TOKEN_INVALID:
                    case ERROR_CODES.AUTH.TOKEN_EMPTY:
                        // 유효하지 않은 토큰
                        toast.error(TOAST_MESSAGES.AUTH.INVALID_TOKEN);
                        await logout();
                        return undefined;
                    
                    default:
                        throw error;
                }
            }
        }
        , [logout]
    );

    return {executeWithAuth};
}