import { apiClient } from "@/config/apiClient";
import { ENV } from "@/config/env";
import { API_ENDPOINTS, TOAST_MESSAGES } from "@/shared/constants";
import { LoginRequest, LoginResponse } from "@/shared/types";

import { encryptPasswordAES, encryptWrapKey, fetchPublicKey, generateAesSymmetricKey, toBase64 } from "@/util/encryption";

/**
 * 로그인
 * @param credentials 
 * @returns 
 */
export async function login(credentials : LoginRequest) : Promise<LoginResponse> {
    if(ENV.IS_DEV) {
        return mockLogin(credentials);
    }   

    try {

        // 1. 서버로부터 공개키 가져오기(TODO 공개키 캐시화? 백엔드 서버 재가동 시 공개키 달라져야 함.)
        const publicKey = await fetchPublicKey(apiClient.defaults.baseURL!);
        
        // 2. AES Key 생성
        const aesKey = await generateAesSymmetricKey();

        // 3. AES Key를 RSA Public Key로 암호화(RSA-OAEP Key Wrapping)
        const encryptedWrapAesKey : Uint8Array = await encryptWrapKey(publicKey, aesKey)
    
        // 4. 패스워드를 암호화한 AES 키로 암호화
        const { encryptedPassword, iv  } = await encryptPasswordAES(credentials.password!, aesKey);

        // 5. Login 시도
        const response = await apiClient.post<LoginResponse>(API_ENDPOINTS.AUTH.LOGIN, {
                userId : credentials.userId
                , encryptedPassword : toBase64(encryptedPassword)
                , encryptedAESKey : toBase64(encryptedWrapAesKey)
                , iv : toBase64(iv)
            } as LoginRequest);

        return response.data;
    }
    catch(error : any) {
        return {
            success : false,
            message : error.response?.data?.message || TOAST_MESSAGES.AUTH.LOGIN_FAIL
        }
    }

}

/**
 * 로그아웃
 * @returns
 */
export async function logout() : Promise<void> {
    if( ENV.IS_DEV) {
        return mockLogout();
    }

    try {
        await apiClient.post(API_ENDPOINTS.AUTH.LOGOUT);
    }
    catch(error) {
        console.error('Logout error : ', error);
    }
}

/**
 * ACCESS_TOKEN 갱신
 */
export async function refreshToken() : Promise<void> {
    await apiClient.post(API_ENDPOINTS.AUTH.REFRESH);
}

/**
 * Mock 로그인
 * @param credentials 
 * @returns 
 */
function mockLogin(credentials : LoginRequest) : LoginResponse {

    if((credentials.userId === 'demo' && credentials.password === 'dummy')) {
        return {
            success : true,
            data : {
                userId : credentials.userId
            }
        }
    }

    return {
        success : false,
        message : TOAST_MESSAGES.AUTH.INVALID_CREDENTIAL
    }
    
}

/**
 * Mock 로그아웃 
 *  - No Action
 */
function mockLogout() : void {
    console.log('Mock logout');
}