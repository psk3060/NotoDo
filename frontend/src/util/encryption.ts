import { ENV } from '@/config/env';
import axios from 'axios';
import forge from "node-forge";

let cachedPublicKey: string | null = null;

/**
 * 서버로부터 RSA 공개키 가져오기
 * @returns 
 */
export async function fetchPublicKey(baseUrl : string) : Promise<string> {

    if( ENV.IS_DEV ) {
        throw new Error('해당 기능은 운영 환경에서만 가능합니다.');
    }

    if( !cachedPublicKey ) {
        try {
            const response = await axios.get(`${baseUrl}/auth/public-key`);
            
            cachedPublicKey = "";

            const data = await response.data;

            if (!data.publicKey) {
                throw new Error('Public key not found in response');
            }

            cachedPublicKey = data.publicKey;
            
            return data.publicKey;

        }
        catch(error) {
            console.error('Error fetching public key:', error);
            throw new Error('Cannot retrieve encryption key from server');

        }
        
    }

    return cachedPublicKey;
}

/**
 * Password 암호화 - RSA
 * @param password 
 * @param publicKeyPem 
 * @returns 
 */
export function encryptPassword(password : string, publicKeyPem : string) : string {

    try {
        const publicKey = forge.pki.publicKeyFromPem(publicKeyPem);

        const encryptedBytes = publicKey.encrypt(password, "RSA-OAEP", {
            md: forge.md.sha256.create(),
            mgf1: { md: forge.md.sha256.create() },
        });

        return forge.util.encode64(encryptedBytes);

    }
    catch(error : any) {
        console.error('Password encryption error:', error);
        throw new Error('Failed to encrypt password');
    }
}

export function clearPublicKeyCache(): void {
    cachedPublicKey = null;
}

/**
 * @TODO AES 대칭키 생성
 * @returns 
 */
export async function generateAesSymmetricKey() : Promise<CryptoKey> {
    
    try {
        const aesKey = await crypto.subtle.generateKey(
                { name : "AES-GCM", length : 256 }
                , true
                , ["encrypt", "decrypt"]
            );
        return aesKey;
    }
    catch(error) {
        console.error("키 생성 실패:", error);
        throw error;
    }
}

/**
 * RSA-OAEP 사용하여 AES 키 암호화
 * @param publicKey : RSA Public Key
 * @param aesKey 
 * @returns 
 */
export async function encryptWrapKey(publicKey : string, aesKey : CryptoKey) : Promise<Uint8Array> {
    const wrappedKey = await crypto.subtle.wrapKey(
        "raw"
        , aesKey
        , await importRsaPublicKey(publicKey)
        , {name : "RSA-OAEP"}
    );

    return new Uint8Array(wrappedKey);
}

/**
 * Public Key를 CryptoKey로 전환
 * @param publicKey 
 * @returns 
 */
export async function importRsaPublicKey(publicKey: string) : Promise<CryptoKey> {
    const keyBuffer = pemToArrayBuffer(publicKey);
    
    return await crypto.subtle.importKey(
        "spki"
        , keyBuffer
        , {
            name : "RSA-OAEP"
            , hash : "SHA-256"
        }
        , false
        , ['wrapKey']
    );
}

function pemToArrayBuffer(publicKey : string) : ArrayBuffer {
    const b64 = publicKey
                    .replace(/-----BEGIN PUBLIC KEY-----/, "")
                    .replace(/-----END PUBLIC KEY-----/, "")
                    .replace(/\s+/g, "");

    const binary = atob(b64);
    const bytes = new Uint8Array(binary.length);

    for(let i = 0; i < binary.length; i++) {
        bytes[i] = binary.charCodeAt(i);
    }

    return bytes.buffer;
}

export async function encryptPasswordAES(password : string, aesKey : CryptoKey) : Promise<{encryptedPassword : Uint8Array; iv : Uint8Array;}> {
    // 1. IV 생성
    const initializationVector = crypto.getRandomValues(new Uint8Array(12));

    const encodePassword = new TextEncoder().encode(password);

    const encryptedData = await crypto.subtle.encrypt(
        {
            name : "AES-GCM"
            , iv : initializationVector
        }
        , aesKey
        , encodePassword
    );

    return {
        encryptedPassword : new Uint8Array(encryptedData)
        , iv : initializationVector
    };
}



export function toBase64(data: Uint8Array): string {
    let binary = "";
    for (let i = 0; i < data.length; i++) {
        binary += String.fromCharCode(data[i]);
    }
    return btoa(binary);
}
