import logging


from model import TokenBlock
from sqlalchemy.ext.asyncio import AsyncSession
from repository.base.base_repository import BaseRepository

logger = logging.getLogger(__name__)

class TokenBaseRepository(BaseRepository):
    
    def __init__(self, session : AsyncSession):
        super().__init__(session)
    
    async def insertBlock(self, user_id, access_jti, refresh_jti, expire_at, event_type):
        """TODO Token 블랙리스트 등록
            조건 : refresh_token 폐기(로그아웃, 신규 로그인)
            로직 : access_token 블랙리스트는 Redis에 등록(TTL 자동 관리, O(1) 조회) - block:access:{jti}
                    expire_at 기준으로 TTL 설정 → 만료된 토큰은 자동 삭제
        """
        entity = TokenBlock(
            userId = user_id,
            accessJti = access_jti,
            refreshJti = refresh_jti,
            expireAt = expire_at,
            eventType = event_type
        )
        
        self.session.add(entity)
        
        await self.session.flush()
        await self.session.refresh(entity)
        
        return entity
        
    
    async def isExistBlock(self):
        '''TODO access_token 검증 미들웨어 + refresh_token 갱신 시 모두 호출'''
        pass
    