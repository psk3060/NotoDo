import axios, { AxiosInstance, InternalAxiosRequestConfig } from "axios";


import {authStore} from "@/features/auth/stores/authStore";
import { ENV } from "@/config/env";

export const apiClient : AxiosInstance = axios.create(
    {
        baseURL : ENV.API_BASE_URL
        , withCredentials: true
        , headers : {
            'Content-Type' : 'application/json'
        }
    }
)

/**
 * Request Interceptor : 크로스체크 userId를 항상 Header에 추가
 */
apiClient.interceptors.request.use((config : InternalAxiosRequestConfig) => {
    const userId = authStore.getState().userId;

    if(userId && config.headers) {
        config.headers!['userId'] = userId;
    }
    return config;
}, (error) => {
    return Promise.reject(error);
});


apiClient.interceptors.response.use(
    (response) => response
    , (error) => {
        if(error.response?.data) {
            return Promise.reject(error);
        }

        return Promise.reject({
            data : {
                code : 'network_error',
                message : '네트워크 오류가 발생했습니다.'
            }
        });
    }
);