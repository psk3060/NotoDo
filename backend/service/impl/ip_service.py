from fastapi import Request
from db.redis import redis_container

import time
import uuid

def get_ip_service():
    return IpService()

class IpService :
    ''' keyPattern
        - blockIpKey = f"block_ip:{ip_address.client_ip}:차단일시"
        - countIpKey = f"fail_ip:{ip}:{id}:등록일시"
    '''
    
    # IP가 Redis에 Block IP로 등록되어 있는지?
    async def exists_block_ip(self, ip: str) -> bool:
        '''
        IP가 메모리 상의 Block IP에 등록되어 있는지?
        '''
        
        pattern = f"block_ip:{ip}:*"
        cursor = 0
        
        while True:
            cursor, keys = await redis_container.ip.scan(cursor=cursor, match=pattern, count=100)
            if keys:  # 하나라도 발견
                return True
            if cursor == 0:
                break

        return False
    
    TRUSTED_PROXIES = {
        "127.0.0.1",     # local nginx
        "10.0.0.1",      # internal LB
        "172.17.0.1",    # docker bridge
    }
    
    def get_real_client_ip(self, request: Request) -> str:
        remote_ip = request.client.host

        # 프록시를 통과한 요청만 Forwarded 신뢰
        if remote_ip in self.TRUSTED_PROXIES:
            xff = request.headers.get("x-forwarded-for")
            if xff:
                # client, proxy1, proxy2
                return xff.split(",")[0].strip()

            xrip = request.headers.get("x-real-ip")
            if xrip:
                return xrip.strip()

        return remote_ip
    
    def get_ip_info(self, request: Request):
        return {
            "client_ip": self.get_real_client_ip(request),
            "remote_ip": request.client.host,
            "xff": request.headers.get("x-forwarded-for"),
            "real_ip": request.headers.get("x-real-ip"),
        }
    
    async def delete_all_fail_ip(self, ip:str) :
        await redis_container.ip.delete(f"fail_ip:{ip}")
        
    
    # IP가 COUNT_IP Redis에 등록되어 있는지? ID 별 합산 제공
    async def debug_fail_by_ip(self, ip: str):
        key = f"fail_ip:{ip}"
        members = await redis_container.ip.zrange(key, 0, -1)

        stats = {}

        for m in members:
            if isinstance(m, bytes):
                m = m.decode()

            user_id = m.split(":", 1)[0]
            stats[user_id] = stats.get(user_id, 0) + 1

        return stats
    
    
    
    async def add_fail_ip(self, ip:str, user_id : str) -> int:
        now = int(time.time())
        key = f"fail_ip:{ip}"
        
        member = f"{user_id}:{now}:{uuid.uuid4().hex}"
        
        pipe = redis_container.ip.pipeline()
        pipe.zadd(key, {member : now}) # 1회 추가
        pipe.zremrangebyscore(key, 0, now - 60) # 1분 이전 제거
        pipe.zcard(key)             # 현재 횟수
        pipe.expire(key, 60)        # TTL 유지
        _, _, count, _ = await pipe.execute()
        
        return count
    
    BLOCK_IP_LUA = """
    redis.call("SET", KEYS[1], 1, "EX", ARGV[1])
    redis.call("DEL", KEYS[2])
    return 1
    """
    
    
    
    async def block_ip(self, ip : str) :
        block_key = f"block_ip:{ip}"
        fail_key = f"fail_ip:{ip}"
        ttl = 3600  # 1시간 차단
        
        block_ip_script = redis_container.ip.register_script(self.BLOCK_IP_LUA)
        
        await block_ip_script(keys=[block_key, fail_key], args=[ttl])