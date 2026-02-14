import { apiClient } from '../config/ApiClient';
import {ENV} from '../config/env';
import { mockResponse } from './mock';
import { fetchPublicKey, generateAesSymmetricKey, encryptWrapKey, encryptPasswordAES } from '../util/encryption';
import type LoginResponse from '../model/LoginResponse';
import type LoginRequest from '../model/LoginRequest';
import localAuthStore from '../store/authStore';

export function toBase64(data: Uint8Array): string {
  let binary = "";
  for (let i = 0; i < data.length; i++) {
    binary += String.fromCharCode(data[i]);
  }
  return btoa(binary);
}

export async function logoutProc() : Promise<boolean> {
    let result : boolean = true;

    const userId = localAuthStore.getState().userId;

    if( ENV.IS_DEV ) {
        result = userId === 'demo';
    }
    else {
        try {
            const res = await apiClient.post<boolean>("/auth/logout");
            return res.data;
        } catch (e) {
            console.error("Logout failed:", e);
            return false;
        }
    }
    return result;
}


export async function loginProc(userId:string, password:string): Promise<{ data: LoginResponse }> {

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

            // WebCrypto API 사용(CryptoJS에서는 OAEP 패딩 제공 안 함)

            // 2. AES Key 생성
            const aesKey = await generateAesSymmetricKey();

            // 3. AES Key를 RSA Public Key로 암호화(RSA-OAEP Key Wrapping)
            const encryptedWrapAesKey : Uint8Array = await encryptWrapKey(publicKey, aesKey)
            
            // 4. 패스워드를 암호화한 AES 키로 암호화
            const { encryptedPassword, iv  } = await encryptPasswordAES(password, aesKey);

            // 5. Login 시도
            result = await apiClient.post<LoginResponse>("/auth/login", {
                userId
                , encryptedPassword : toBase64(encryptedPassword)
                , encryptedAESKey : toBase64(encryptedWrapAesKey)
                , iv : toBase64(iv)
            } as LoginRequest);
           
        } catch(error: any) {
            console.error('Login service error:', error);
        
            // 에러 응답 처리
            if (error.response) {
                result = {
                            data: {
                                success: false,
                                message: error.response.data?.detail || '아이디 또는 비밀번호를 찾을 수 없습니다.'
                            }
                        };
            }

        }
    }

    return result;
}




