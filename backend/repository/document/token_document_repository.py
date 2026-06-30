from datetime import datetime

from model import RefreshTokenLogDocument, RefreshTokenLogDTO

class TokenDocumentRepository:
    
    async def insert(self, dto: RefreshTokenLogDTO):
        '''Refresh Token 로그 저장'''
        await RefreshTokenLogDocument(**dto.model_dump(), revoked=False).insert()
    
    
    async def revoke(self, revoke_reason : str, user_id : str, refresh_token_hash : str | None = None, refresh_token_jti : str | None = None) :
        '''토큰 폐기'''
        tokens = None
        
        # 로그아웃, 재발급으로 인한 refresh_token revoke
        if revoke_reason in ['refresh', 'logout'] :
            tokens = await RefreshTokenLogDocument.find(
                RefreshTokenLogDocument.user_id == user_id,
                RefreshTokenLogDocument.refresh_token_hash == refresh_token_hash,
                RefreshTokenLogDocument.refresh_token_jti == refresh_token_jti,
                RefreshTokenLogDocument.revoked == False
            ).to_list()
        # 로그인 시 기존 refresh_token 모두 revoke
        else :
            tokens = await RefreshTokenLogDocument.find(
                RefreshTokenLogDocument.user_id == user_id,
                RefreshTokenLogDocument.revoked == False
            ).to_list()
        
        for t in tokens:
            t.revoked = True
            t.revoked_at = datetime.now().isoformat()
            t.revoked_reason = revoke_reason
            
            await t.save()
            