import axios from "axios";

import localAuthStore from '../store/authStore';

export const apiClient = axios.create(
    {
        baseURL : 'http://localhost:8000'
        , withCredentials: true
    }
)

apiClient.interceptors.request.use(config => {
    const userId = localAuthStore.getState().userId; // 항상 최신 값
    if(userId) config.headers!['userId'] = userId;
    return config;
});
