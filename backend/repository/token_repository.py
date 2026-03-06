import datetime

from datetime import datetime

from model.auth.refresh_token_log import RefreshTokenLog, RefreshTokenLogDTO

class RefreshTokenLogRepository:
    
    async def insert(self, dto: RefreshTokenLogDTO):
        await RefreshTokenLog(**dto.model_dump(), revoked=False).insert()
    
    
    async def revoke(self, revoke_reason : str, user_id : str, token_hash : str | None = None, jti : str | None = None) :
        tokens = None
        
        # 로그아웃, 재발급으로 인한 refresh_token revoke
        if revoke_reason in ['refresh', 'logout'] :
            tokens = await RefreshTokenLog.find(
                RefreshTokenLog.user_id == user_id,
                RefreshTokenLog.token_hash == token_hash,
                RefreshTokenLog.jti == jti,
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
            