import {create} from 'zustand';
import {createJSONStorage, persist} from 'zustand/middleware';

import {STORAGE_KEYS} from '@/shared/constants'
import { AuthStore } from '@/shared/types';

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