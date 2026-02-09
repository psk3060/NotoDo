import { apiClient } from '../config/ApiClient';
import {ENV} from '../config/env';
import { mockResponse } from './mock';
import { fetchPublicKey, encryptPassword } from '../util/encryption';
import type LoginResponse from '../model/LoginResponse';

interface LoginRequest {
    userId: string;
    encryptedPassword: string;
}



export async function loginService(userId:string, password:string): Promise<{ data: LoginResponse }> {

    let result: any;

    if( ENV.IS_DEV ) {
        result = mockResponse({
            success : (userId === 'demo' && password === 'dummy')
            , message : (userId === 'demo' && password === 'dummy') ? '로그인 성공' : '아이디 또는 비밀번호를 찾을 수 없습니다.'
        });
    }
    else {

        try {

            // 1. 서버로부터 공개키 가져오기
            const publicKey = await fetchPublicKey(apiClient.defaults.baseURL!);

            // 2. 비밀번호 암호화 TODO
            const encryptedPassword = encryptPassword(password, publicKey);

            // 3. 로그인 시도(TODO Token 발급)
            result = await apiClient.post<LoginResponse>("/auth/login", {userId, encryptedPassword} as LoginRequest);
           
        } catch(error: any) {
            console.error('Login service error:', error);
        
            // 에러 응답 처리
            if (error.response) {
                result = {
                            data: {
                                success: false,
                                message: error.response.data?.detail || 'Login failed'
                            }
                        };
            }

        }
    }

    return result;
}




