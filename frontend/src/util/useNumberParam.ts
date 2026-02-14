import { useParams } from "react-router-dom";

export function useNumberParam(name: string) : number {
    const params = useParams();
    const value = params[name];

    if (!value) {
        throw new Error(`${name} 파라미터가 없습니다`);
    }

    const num = parseInt(value, 10);

    if (Number.isNaN(num)) {
        throw new Error(`${name}는 숫자여야 합니다`);
    }

    return num;
}