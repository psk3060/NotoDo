import {create} from 'zustand';
import {createJSONStorage, persist} from 'zustand/middleware';

interface AuthStore {
    userId : string | null;
    isAuthenticated : boolean;
    setUserId : (userId : string) => void;
    setAuthenticated : (isAuthenticated : boolean) => void;
    /*
    setAccessToken : (token : string) => void;
    setRefreshToken : (token : string) => void;
    */
}

const localAuthStore = create<AuthStore>()(
    persist(
        (set, _) => ({
            // TODO Token 발급 이후 제거
            userId: null,
            // Front Display 위한 변수(제거하지 않기)
            isAuthenticated : true,
            setUserId : (userId : string) => {
                set(_ => ({userId}))
            },
            setAuthenticated : (isAuthenticated : boolean) => {
                set(_ => ({isAuthenticated}))
            }
        })
        , {
            name: "auth-store"
            , storage: createJSONStorage(() => localStorage)
            , version: 1
        }
    )
);

export default localAuthStore;