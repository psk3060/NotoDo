import axios from "axios";

import localAuthStore from '../store/authStore';

const userId = localAuthStore.getState().userId;

export const apiClient = axios.create(
    {
        baseURL : 'http://localhost:8000'
        , withCredentials: true
        , headers : {
            "userId" : userId
        }
    }
)
