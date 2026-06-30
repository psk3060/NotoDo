export interface ApiError {
    code : string;
    message : string;
    status? : number;
}

export interface ApiResponse<T> {
    data : T;
    success : boolean;
    message? : string;
}

export interface HttpApiError {
    response?: {
        data?: {
            code?: string;
            message?: string;
        };
    };
}

export interface PagedResponse<T> {
    data: T[];
    total: number;  // 전체 개수
    message? : string;
    totalPages : number;
}

export interface SearchParam {
    title: string,
    status: string,
    priority: string,
}

export interface FrequentlyConditionSearchParam {
    selectedId? : string;
    title?: string;
    status?: string;
    priority?: string;
}

export interface ModalProps {
    isOpen : boolean;
    onClose : () => void;
    onApply : (condition: SearchParam) => void;
}

// 자주 사용하는 단어, 문구에 대한 인터페이스 정의(무조건 5개만 조회)
export interface FrequentlyConditionResponse<T> {
    data: T[];
    message? : string;
}