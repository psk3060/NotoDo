export function dateToString(dateParam: Date): string {

    return `${dateParam.getFullYear()}년 ${dateParam.getMonth() + 1}월 ${dateParam.getDate()}일 ${dateParam.getHours() > 12 ? '오후' : '오전'} ${dateParam.getHours() % 12}:${dateParam.getMinutes() < 10 ? '0' + dateParam.getMinutes() : dateParam.getMinutes()}`;

}