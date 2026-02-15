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
        INVALID_TOKEN : '토큰이 유효하지 않거나 비어 있습니다. 재로그인 해주세요.',
        LOGIN_ERROR : '로그인 처리 중 오류가 발생했습니다.',
        LOGIN_FAIL : '로그인에 실패했습니다.',
        INVALID_CREDENTIAL : '아이디 또는 비밀번호가 일치하지 않습니다.'
    },
    TODO : {
        CREATE_SUCCESS : 'Todo가 생성되었습니다.',
        UPDATE_SUCCESS : 'Todo가 수정되었습니다.',
        DELETE_SUCCESS : 'Todo가 삭제되었습니다.',
        FETCH_ALL_FAIL : 'Todo 목록을 불러오는데 실패했습니다.',
        DELETE_FAIL : 'Todo 삭제에 실패했습니다.',
        FETCH_FAIL : 'Todo를 불러오는데 실패했습니다.',
        CREATE_FAIL : 'Todo 생성에 실패했습니다.',
        UPDATE_FAIL : 'Todo 수정에 실패했습니다.',
    }
} as const;

export const ERROR_CODES = {
    AUTH : {
        TOKEN_EXPIRED : 'expired',
        TOKEN_INVALID : 'invalid',
        TOKEN_EMPTY : 'empty_token'
    }
} as const;