import moment from 'moment';

export function formatDateTime(date : Date): string {
    return moment(date).format('YYYY-MM-DD HH:mm');
}

export function getCurrentTimestamp() : string {
    return formatDateTime(new Date());
}

export function formatDate(date : Date) : string {
    return moment(date).format('YYYY-MM-DD');
}

/**
 * 날짜 문자열의 유효성을 체크
 * @param dateString 
 * @returns 
 */
export function isValidDate(dateString : string) : boolean {
    return moment(dateString).isValid();
}

/**
 * 현재 시간을 KST 시간 포맷(년월일오전/오후시분)으로 출력
 * @returns 
 */
export function getCurrentTimestampKST() : string {
    return toKSTString(new Date());
}

/**
 * Date 객체를 KST 시간 포맷(년월일오전/오후시분)으로 출력
 * @param date 
 * @returns 
 */
export function toKSTString(date: Date): string {
    const formatter = new Intl.DateTimeFormat('ko-KR', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: 'numeric',
        minute: '2-digit',
        hour12: true
    });

    return formatter.format(date);
}