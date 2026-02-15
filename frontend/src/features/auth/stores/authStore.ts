import {create} from 'zustand';
import {createJSONStorage, persist} from 'zustand/middleware';

import {STORAGE_KEYS} from '@/shared/constants'
import { AuthStore } from '@/shared/types/auth';

export const authStore = create<AuthStore>()(
    persist(
        (set) => ({
            userId: null,
            isAuthenticated : false,
            setUserId : (userId : string) => {
                set({userId})
            },
            setAuthenticated : (isAuthenticated : boolean) => {
                set({isAuthenticated})
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
