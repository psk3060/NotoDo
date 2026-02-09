import axios from 'axios';
import forge from "node-forge";
import {ENV} from '../config/env';

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