import { useParams } from "react-router-dom";

/**
 * URL 파라미터에서 숫자를 추출하는 커스텀 훅
 * @param paramName 
 */
export function useNumberParam(paramName : string) : number {
    const params = useParams<{[key : string] : string}>();
    const value = params[paramName];

    if(!value) return 0;

    const parsed = parseInt(value, 10);
    return isNaN(parsed) ? 0 : parsed;

}

/**
 * URL 파라미터에서 문자열을 추출하는 커스텀 훅
 * @param paramName 
 * @returns 
 */
export function useStringParam(paramName : string) : string | undefined {
    const params = useParams<{[key : string] : string}>();
    return params[paramName];
}
