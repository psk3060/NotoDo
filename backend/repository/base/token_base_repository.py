class TokenBaseRepository:
    async def insertBlock(self):
        '''TODO 로그아웃 및 해당 ID 신규 로그인 시 refresh_token 블랙리스트 등록
            access_token 블랙리스트는 Redis에 등록(TTL 자동 관리, O(1) 조회) - block:access:{jti}
           expire_at 기준으로 TTL 설정 → 만료된 토큰은 자동 삭제'''
        pass
    
    async def isExistBlock(self):
        '''TODO access_token 검증 미들웨어 + refresh_token 갱신 시 모두 호출'''
        pass
    