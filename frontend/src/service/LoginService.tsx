import { apiClient } from '../config/ApiClient';
import {ENV} from '../config/env';
import { mockResponse } from './mock';

export async function loginService(userId:string, password:string) {

    let result: any;

    if( ENV.IS_DEV ) {
        result = mockResponse((userId === 'demo' && password === 'dummy'));
    }
    else {
        result = apiClient.post("/auth/login", {userId, password});
        
    }

    return result;
}