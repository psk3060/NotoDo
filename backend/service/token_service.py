import os, jwt, uuid, logging

from typing import Any

from abc import ABC, abstractmethod
from fastapi import HTTPException, Response, Request
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone

from model import RefreshTokenLogDTO
from repository import TokenDocumentRepository, TokenBaseRepository

from core.redis_container import redis_container

from utils.string_utils import replace_hash_string

load_dotenv()

logger = logging.getLogger(__name__)

def get_token_service(token_type : str | None = 'jwt'):
    # token_type 환경변수로
    if token_type == 'jwt':
        return JwtTokenServiceImpl(token_document_repository=TokenDocumentRepository(), token_base_repository=TokenBaseRepository())
    

class TokenService(ABC):
    
    def __init__(self, token_document_repository: TokenDocumentRepository, token_base_repository : TokenBaseRepository):
        self.token_document_repository = token_document_repository
        self.token_base_repository = token_base_repository

    # Token 저장 - 로그인 
    @abstractmethod
    def saveToken(self, user_id : str, issued_type : str, request : Request, response : Response) : ...
    
    # 해당 회원의 모든 refresh token 폐기 - 로그인 시 
    @abstractmethod
    def revoke_user_refresh_tokens(self, user_id: str): ...
    
    # 해당 refresh token 폐기
    @abstractmethod
    def revoke_refresh_token(self, refresh_token : str): ...
    
    # refresh token 재발급
    @abstractmethod
    async def reissue_refresh_token(self, refresh_token : str, request : Request, response : Response) : ...
    
    @abstractmethod
    async def regist_black(self, access_token : str, refresh_token : str, event_type : str = "logout"): ...
    
    def saveCookie(self, token_type : str, token : str, response : Response) : 
        """쿠키에 저장
        - JWT 일 경우에만 전재"""
        key = f"{token_type.lower()}_token"
        
        max_age = 60 * 15
        token_path = "/"
        
        if token_type == "refresh":
            max_age = 7 * 24 * 3600
            token_path = "/auth"
            
        
        # 토큰을 Cookie에 저장
        response.set_cookie(
            key=key,
            value=token,
            httponly=True,
            secure=os.getenv('TODO_ENV') == "prod",
            max_age=max_age,
            samesite="lax",
            path=token_path
        )
    
    
class JwtTokenServiceImpl(TokenService):
    """JWT 기반 토큰 서비스
    """
    
    
    def jwt_payload_decode(self, token : str, secret_key : str) -> dict[str, Any]: 
        """jwt 기반 payload로 decode"""
        token_algorithm = os.getenv('TOKEN_ALGORITHM', '') 

        try :
            if not secret_key or secret_key == "":
                raise Exception("SECRET_KEY가 설정되지 않았습니다.")
            
            if not token_algorithm or token_algorithm == "":
                raise Exception("토큰 알고리즘이 설정되지 않았습니다.")
            
            return jwt.decode(token, secret_key, algorithms=[token_algorithm])
            
        except Exception as e:
            raise e
        
    
    def encodeToken(self, user_id : str, token_type : str, secret_key : str) -> str:
        '''Token(Access, Refresh) 인코딩'''
        
        try:
            
            if not secret_key or secret_key == "":
                raise Exception(f"{token_type.upper()} SECRET_KEY 환경변수가 설정되지 않았습니다.")
            
            token_algorithm = os.getenv('TOKEN_ALGORITHM', '')
        
            if not token_algorithm or token_algorithm == "":
                raise Exception("TOKEN_ALGORITHM 환경변수가 설정되지 않았습니다.")
            
        except Exception as e:
            logger.critical(e)
            raise HTTPException(
                status_code=500,
                detail= "서버 설정 오류입니다."
            )
            
        
        if token_type == "access":
            expire = datetime.now(timezone.utc) + timedelta(minutes=15)
        elif token_type == "refresh":
            expire = datetime.now(timezone.utc) + timedelta(days=7)
        else :
            raise HTTPException(
                status_code=400,
                detail="잘못된 토큰 타입입니다."
            )
        
        payload = {
            "user_id": user_id,
            "exp": expire,
            "type" : token_type,
            "iat" : datetime.now(timezone.utc),
            "jti": str(uuid.uuid4()),
            "sid" : str(uuid.uuid4()),
            "iss" : os.getenv('TOKEN_ISSUER', 'localhost')
        }
        
        headers = {
            "kid": str(uuid.uuid4())
        }
        
        return jwt.encode(payload, secret_key, algorithm=token_algorithm, headers = headers)
        
    
    def generateTokenPair(self, user_id : str) -> dict[str] :
        """토큰 생성"""
        result = {}
        
        try :
            # 1. Refresh Token 생성
            refresh_token = self.encodeToken(user_id, 'refresh', os.getenv('REFRESH_TOKEN_SECRET_KEY', ''))
            
            # 2. Access Token 생성
            access_token = self.encodeToken(user_id, 'access', os.getenv('ACCESS_TOKEN_SECRET_KEY', ''))
            
            if not refresh_token or refresh_token == "":
                raise Exception("refresh_token이 생성되지 않았습니다.")
            
            if not access_token or access_token == "":
                raise Exception("access_token이 생성되지 않았습니다.")
            
            result['access_token'] = access_token
            result['refresh_token'] = refresh_token
            
        except Exception as e:
            
            result = {}
            
            logger.error(e)
            
            raise HTTPException(
                status_code=500,
                detail= "서버 오류입니다."
            )
        
        return result
    
    async def regist_black(self, access_token : str, refresh_token : str, event_type : str = "logout"):
        """ 해당 토큰을 black 리스트에 등록
        token jti (expire_at - 현재시각)만큼 ttl 설정하여 블랙리스트에 등록
        celery worker 등록하여 처리 할지 검토"""
        # payload 얻기(토큰 유형, 만료 시간, 회원ID, jti 등이 보관)
        
        access_token_payload = self.jwt_payload_decode(access_token, os.getenv('ACCESS_TOKEN_SECRET_KEY'))
        refresh_token_payload = self.jwt_payload_decode(refresh_token, os.getenv('REFRESH_TOKEN_SECRET_KEY'))
        
        access_user_id = access_token_payload['user_id']
        refresh_user_id = refresh_token_payload['user_id']
        
        if access_user_id != refresh_user_id:
            raise HTTPException(
                status_code=400,
                detail="Token의 사용자 ID가 올바르지 않습니다."
            )

        # TODO : 블랙리스트 등록 로직 구현 및 파라미터 정리(DB에 등록)
        await self.token_base_repository.insertBlock(access_user_id, access_token_payload['jti'], refresh_token_payload['jti'], refresh_token_payload['exp'], event_type)
        
        # TODO : Redis에 access_token 블랙리스트 등록(만료시간 기준으로 TTL 설정)
        
        
        
        await self.token_base_repository.commit()
        
        
        
        
        
    async def saveToken(self, user_id : str, issued_type : str, request : Request, response : Response) -> dict[str] :
        
        ''' Token 생성
            1. 생성 기준
                - 로그인 할 때마다(기존 모두 미사용 처리 이후 신규 발급)
                - Refresh Token 갱신 할 때마다
            2. 세션 정책 : 단일 세션 정책(전부 제거)
                - 다중 세션 정책 → 동일 device_id만 제거(다중 디바이스 관리 시)
            3. DB 별 Refresh Token 관점(Refresh Token은 Hash 값만 저장)
                - Redis : 세션 접근(성능), TTL 설정
                - PostgreSQL : 세션 관리(이력 관리 / 권한 관리)
            4. Cookie 저장 옵션 : Secure=True, SameSite=Lax, HttpOnly
        '''
        
        token_pair = self.generateTokenPair(user_id)
        
        refresh_token = token_pair["refresh_token"]
        access_token = token_pair["access_token"]
        
        
        # payload 조회
        refresh_payload = self.jwt_payload_decode(refresh_token, os.getenv('REFRESH_TOKEN_SECRET_KEY'))
        access_payload = self.jwt_payload_decode(access_token, os.getenv('ACCESS_TOKEN_SECRET_KEY'))
        
        # refresh token의 user_id
        payload_user_id = refresh_payload['user_id']
        
        # 해시 생성
        refresh_token_hash = replace_hash_string(refresh_token)
        key = f"refresh:{payload_user_id}:{refresh_payload['jti']}"
        
        # Redis에 저장(TTL = 7일)
        await redis_container.refresh.set(key, refresh_token_hash, ex=60*60*24*7)
        
        await self.token_document_repository.insert(
            RefreshTokenLogDTO(
                user_id = user_id
                , refresh_token_hash = refresh_token_hash
                , refresh_token_jti = refresh_payload['jti']
                , access_token_hash = replace_hash_string(access_token)
                , access_token_jti = access_payload['jti']
                , issued_at = datetime.fromtimestamp(refresh_payload["iat"]).isoformat()
                , expires_at=datetime.fromtimestamp(refresh_payload["exp"]).isoformat()
                , ip=request.client.host if request else None
                , user_agent=request.headers.get("user-agent") if request else None
                , issued_type=issued_type
            )
        ) 
        
        # Save Cookie
        self.saveCookie('access', access_token, response)
        self.saveCookie('refresh', refresh_token, response)
        
    
    async def revoke_user_refresh_tokens(self, user_id: str):
        """사용자 기준 - 기존 refresh token 폐기(로그아웃 생략 대비)"""
        pattern = f"refresh:{user_id}:*"
        cursor = 0
        keys_to_delete = []

        while True:
            cursor, keys = await redis_container.refresh.scan(cursor=cursor, match=pattern, count=100)
            
            keys_to_delete.extend(keys)
            
            if cursor == 0:
                break
        
        if keys_to_delete:
            await redis_container.refresh.delete(*keys_to_delete)
        
        await self.token_document_repository.revoke(revoke_reason="login", user_id = user_id)
        
    
    async def revoke_refresh_token(self, refresh_token : str):
        """refresh token 폐기"""
        
        try :
            refresh_token_hash = replace_hash_string(refresh_token)
            
            payload = self.jwt_payload_decode(refresh_token, os.getenv('REFRESH_TOKEN_SECRET_KEY', ''))
        
            key = f"refresh:{payload['user_id']}:{payload['jti']}"
            
            stored_hash = await redis_container.refresh.get(key)
            
            if stored_hash is None:
                raise Exception("Refresh Token이 존재하지 않습니다.")

            if isinstance(stored_hash, bytes):
                stored_hash = stored_hash.decode()

            if stored_hash != refresh_token_hash:
                raise Exception("Refresh Token이 일치하지 않습니다.")
            
            user_id = payload.get("user_id")
            
            await self.token_document_repository.revoke(revoke_reason = "logout", user_id=user_id, refresh_token_hash = refresh_token_hash, refresh_token_jti = payload['jti'])
            
        except Exception as e:
            print(e)
    
    
    
    async def reissue_refresh_token(self, refresh_token : str, request : Request, response : Response) :
        """refresh token 재발급"""
        try :
            refresh_token_hash : str = replace_hash_string(refresh_token)
            
            payload = self.jwt_payload_decode(refresh_token, os.getenv('REFRESH_TOKEN_SECRET_KEY', ''))
            
            key = f"refresh:{payload['user_id']}:{payload['jti']}"
            
            stored_hash = await redis_container.refresh.get(key)
            
            if stored_hash is None:
                raise Exception("Refresh Token이 존재하지 않습니다.")

            if isinstance(stored_hash, bytes):
                stored_hash = stored_hash.decode()

            if stored_hash != refresh_token_hash:
                raise Exception("Refresh Token이 일치하지 않습니다.")
            
            user_id = payload.get("user_id")
            
            await self.token_document_repository.revoke(revoke_reason = "refresh", user_id=user_id, refresh_token_hash = refresh_token_hash, refresh_token_jti = payload['jti'])
            
            # 토큰 발급(DB, Redis, 쿠키에 저장하는 로직도 있기 때문에 saveToken)
            await self.saveToken(user_id, 'refresh', request, response)
            
        except Exception as e:
            raise e
        finally :
            # TODO (expire_at - 현재시각) ttl 설정하여 Refresh 토큰을 블랙리스트에 등록
            logger.info("블랙리스트에 등록 완료")
    
    