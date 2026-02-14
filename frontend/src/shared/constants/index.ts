// API ENDPOINT
export const API_ENDPOINTS = {
    AUTH : {
        LOGIN : '/auth/login',
        LOGOUT : '/auth/logout',
        REFRESH : '/auth/refresh'
    },
    TODOS : {
        BASE : '/todos',
        BY_ID : (id : number) => `/todos/${id}`
    }
} as const;


// Routes
export const ROUTES = {
    HOME : '/',
    LOGIN : '/login',
    TODOS : '/todos',
    TODO_DETAIL : (id : number) => `/todos/${id}`
} as const;


// Storage keys
export const STORAGE_KEYS = {
    AUTH : 'auth-store',
    LOCAL_TODO : 'local-todo-store'
} as const;

// Todo Status
export const TODO_STATUS = {
    PENDING : 'Pending',
    IN_PROGRESS : 'In Progress',
    COMPLETED : 'Completed'
} as const;

export const TOAST_MESSAGES = {
    AUTH : {
        LOGIN_REQUIRED : '재로그인이 필요합니다.',
        INVALID_TOKEN : '토큰이 유효하지 않거나 비어 있습니다. 재로그인 해주세요.'
    },
    TODO : {
        CREATE_SUCCESS : '',
        UPDATE_SUCCESS : '',
        DELETE_SUCCESS : '',
    }
} as const;

export const ERROR_CODES = {
    AUTH : {
        TOKEN_EXPIRED : 'expired',
        TOKEN_INVALID : 'invalid',
        TOKEN_EMPTY : 'token_empty'
    }
} as const;