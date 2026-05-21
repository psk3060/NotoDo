import datetime

from datetime import datetime

from model.auth.refresh_token_log import RefreshTokenLog, RefreshTokenLogDTO

class TokenRepository:
    async def insertBlock(self):
        '''TODO 로그아웃 및 해당 ID 신규 로그인 시 refresh_token 블랙리스트 등록
            access_token 블랙리스트는 Redis에 등록(TTL 자동 관리, O(1) 조회) - block:access:{jti}
           expire_at 기준으로 TTL 설정 → 만료된 토큰은 자동 삭제'''
        pass
    
    async def isExistBlock(self):
        '''TODO access_token 검증 미들웨어 + refresh_token 갱신 시 모두 호출'''
        pass
    

class LoginHistoryRepository:
    '''로그인 이력 History
        attempted_at
        user_id
        success
        실패했을 경우 - failure_reason
        성공 시 access_token.jti 보관
        refresh_token.jti : 관리자가 직접 관여
        
        ip_address
        
        Index 검토
        - user_id + attempted_at 특정 유저의 로그인 이력 조회
        - ip_address : IP 기반 이상 탐지
        - access_token_jti : 토큰 추적
        
        로그인 이력을 얼마나 보관할지? 90일? 1년? NoSQL의 TTL 인덱시 기능으로 자동 삭제 처리
    '''
    
    pass

class RefreshTokenLogRepository:
    
    async def insert(self, dto: RefreshTokenLogDTO):
        await RefreshTokenLog(**dto.model_dump(), revoked=False).insert()
    
    
    async def revoke(self, revoke_reason : str, user_id : str, refresh_token_hash : str | None = None, refresh_token_jti : str | None = None) :
        tokens = None
        
        # 로그아웃, 재발급으로 인한 refresh_token revoke
        if revoke_reason in ['refresh', 'logout'] :
            tokens = await RefreshTokenLog.find(
                RefreshTokenLog.user_id == user_id,
                RefreshTokenLog.refresh_token_hash == refresh_token_hash,
                RefreshTokenLog.refresh_token_jti == refresh_token_jti,
                RefreshTokenLog.revoked == False
            ).to_list()
        # 로그인 시 기존 refresh_token 모두 revoke
        else :
            tokens = await RefreshTokenLog.find(
                RefreshTokenLog.user_id == user_id,
                RefreshTokenLog.revoked == False
            ).to_list()
        
        for t in tokens:
            t.revoked = True
            t.revoked_at = datetime.now().isoformat()
            t.revoked_reason = revoke_reason
            
            await t.save()
            