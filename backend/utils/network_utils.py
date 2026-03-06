from fastapi import Request

TRUSTED_PROXIES = {
        "127.0.0.1",     # local nginx
        "10.0.0.1",      # internal LB
        "172.17.0.1",    # docker bridge
}

def get_real_client_ip(request: Request) -> str:
    remote_ip = request.client.host

    # 프록시를 통과한 요청만 Forwarded 신뢰
    if remote_ip in TRUSTED_PROXIES:
        xff = request.headers.get("x-forwarded-for")
        
        if xff:
            # client, proxy1, proxy2
            return xff.split(",")[0].strip()

        xrip = request.headers.get("x-real-ip")
        if xrip:
            return xrip.strip()

        return remote_ip
    
def get_ip_info(request: Request):
    return {
        "client_ip": get_real_client_ip(request),
        "remote_ip": request.client.host,
        "xff": request.headers.get("x-forwarded-for"),
        "real_ip": request.headers.get("x-real-ip"),
    }
    