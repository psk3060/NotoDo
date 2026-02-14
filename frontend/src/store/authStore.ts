import {create} from 'zustand';
import {createJSONStorage, persist} from 'zustand/middleware';

import {STORAGE_KEYS} from '@/shared/constants'

interface AuthStore {
    userId : string | null;
    isAuthenticated : boolean;
    setUserId : (userId : string) => void;
    setAuthenticated : (isAuthenticated : boolean) => void;
    clearAuth : () => void;
}

const localAuthStore = create<AuthStore>()(
    persist(
        (set, _) => ({
            userId: null,
            // Front Display 위한 변수(제거하지 않기)
            isAuthenticated : true,
            setUserId : (userId : string) => {
                set(_ => ({userId}))
            },
            setAuthenticated : (isAuthenticated : boolean) => {
                set(_ => ({isAuthenticated}))
            },
            clearAuth : () => set({
                userId : null,
                isAuthenticated : false
            })
        })
        , {
            name: STORAGE_KEYS.AUTH
            , storage: createJSONStorage(() => localStorage)
            , version: 1
        }
    )
);

export default localAuthStore;