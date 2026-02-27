// API ENDPOINT
export const API_ENDPOINTS = {
    AUTH : {
        LOGIN : '/auth/login',
        LOGOUT : '/auth/logout',
        REFRESH : '/auth/refresh'
    },
    TODOS : {
        BASE : '/todos',
        COMMENT : (id : string) => `/todos/${id}/comments`,
        BY_ID : (id : string) => `/todos/${id}`
    }
} as const;


// Routes
export const ROUTES = {
    HOME : '/',
    LOGIN : '/login',
    TODOS : '/todos',
    TODO_DETAIL : (id : string) => `/todos/${id}`
} as const;


// Storage keys
export const STORAGE_KEYS = {
    AUTH : 'auth-store',
    LOCAL_TODO : 'local-todo-store'
} as const;

// Todo Status
export const TODO_STATUS = {
    PENDING : 'PENDING',
    IN_PROGRESS : 'IN_PROGRESS',
    COMPLETED : 'COMPLETED'
} as const;

export type TodoStatus = typeof TODO_STATUS[keyof typeof TODO_STATUS];

export const TODO_STATUS_LABEL: Record<TodoStatus, string> = {
  PENDING: '미시작',
  IN_PROGRESS: '진행중',
  COMPLETED: '완료'
};

export const DEFAULT_TODO_STATUS = TODO_STATUS.PENDING;


export const TODO_PRIORITY = {
  URGENT: 'P1',
  HIGH: 'P2',
  MEDIUM: 'P3',
  LOW: 'P4',
  VERY_LOW: 'P5'
} as const;

export type TodoPriority = typeof TODO_PRIORITY[keyof typeof TODO_PRIORITY];

export const TODO_PRIORITY_LABEL: Record<TodoPriority, string> = {
  P1: '긴급',
  P2: '높음',
  P3: '중간',
  P4: '낮음',
  P5: '매우 낮음'
};

export const DEFAULT_TODO_PRIORITY = TODO_PRIORITY.MEDIUM;

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
        CREATE_COMMENT_SUCCESS : 'Todo 답글이 생성되었습니다.',
        UPDATE_SUCCESS : 'Todo가 수정되었습니다.',
        DELETE_SUCCESS : 'Todo가 삭제되었습니다.',
        FETCH_ALL_FAIL : 'Todo 목록을 불러오는데 실패했습니다.',
        DELETE_FAIL : 'Todo 삭제에 실패했습니다.',
        FETCH_FAIL : 'Todo를 불러오는데 실패했습니다.',
        CREATE_FAIL : 'Todo 생성에 실패했습니다.',
        CREATE_COMMENT_FAIL : 'Todo 답글 생성에 실패했습니다.',
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