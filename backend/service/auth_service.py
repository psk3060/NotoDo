import logging

from core.rsa_mamanger import rsa_manager

from fastapi import HTTPException, Response, Request

from abc import ABC, abstractmethod
from utils import network_utils
from service.ip_service import IpService
from service.token_service import TokenService
from service.user_service import UserServiceImpl
from model import LoginRequest, LoginResponse

from utils.security_utils import verify_password

logger = logging.getLogger(__name__)

class AuthService(ABC):
    '''SocialAuthServiceImpl도 추가 가능'''
    @abstractmethod
    def login(loginRequest : LoginRequest, request: Request, response: Response) -> LoginResponse:
        pass
    
    @abstractmethod
    def logout(request : Request, response : Response):
        pass
    

class TokenAuthServiceImpl(AuthService):
    
    '''토큰 기반 인증 서비스'''
    def __init__(self, token_service : TokenService, user_service : UserServiceImpl, ip_service : IpService) :
        self.token_service = token_service
        self.user_service = user_service
        self.ip_service = ip_service
    
    
    async def login(self, loginRequest : LoginRequest, request: Request, response: Response) -> LoginResponse:
        '''Login 처리 메소드
            1. IP 체크(5회) - 잠김 여부 파악
            2. 패스워드 복호화(RSA + AES 하이브리드)
            3. Token 발급 정책
                - Access Token : 로그인 할 때마다 
                - Refresh Token : 갱신 하였을 경우
            
        '''
        
        isSuccess : bool = False
        returnMsg : str = ""
        
        ip_dict = network_utils.get_ip_info(request)
        
        ip = ''
        
        if 'client_ip' in ip_dict:
            ip = ip_dict['client_ip']
        
        
        try:
            if not ip or ip == '':
                raise Exception("Client IP가 비어있습니다.")
            
            if await self.ip_service.exists_block_ip(ip):
                raise Exception(f"해당 IP({ip})는 차단된 IP 입니다.")
            
            user = await self.user_service.find_by_id(loginRequest.userId)
            
            if not user:
                raise ValueError("User not found in DB")
            
            plain_password = await rsa_manager.decrypt_password_AES(loginRequest)
            
            isSuccess = verify_password(plain_password, user.password)
            
            if not isSuccess:
                raise ValueError("비밀번호가 올바르지 않습니다.")
            
            # 기존 refresh_token 모두 revoke
            await self.token_service.revoke_user_refresh_tokens(loginRequest.userId)
            
            # 신규 토큰 발급 및 저장
            await self.token_service.saveToken(loginRequest.userId, 'login', request, response)
            
            
            
            # IP COUNT 초기화 - 성공 시
            await self.ip_service.delete_ip(ip)
            
        except (ValueError, HTTPException) as ve :
            # 회원정보 찾을 수 없을 경우에는 Exception과 별도
            logger.fatal(ve)
            isSuccess = False
            
            # 실패 카운트 - 회원ID 별
            count = await self.ip_service.regist_fail_ip(ip, loginRequest.userId)
            
            # 5 이상일 경우 IP 차단
            if count is not None and count >= 5:
                await self.ip_service.regist_block_ip(ip)
            
            returnMsg = "아이디 또는 비밀번호를 찾을 수 없습니다."
            
        except Exception as e:
            logger.critical(e)
            isSuccess = False
            returnMsg = "아이디 또는 비밀번호를 찾을 수 없습니다."
    
        return LoginResponse(success = isSuccess, message = returnMsg)
        
    
    async def logout(self, request, response) -> None:
        refresh_token = request.cookies.get("refresh_token")

        try :
            # Refresh Token 있을 경우
            if refresh_token:
                await self.token_service.revoke_refresh_token(refresh_token)
        except Exception as e:
            logger.error(f"refresh token revoke 실패: {e}")
        finally:
            # 쿠키 삭제는 무조건 이뤄져야 함.
            self.deleteCookie(response)





    def deleteCookie(self, response: Response) :
        '''Token 삭제
                - 삭제 기준 : 로그아웃 할 때마다'''

        # 쿠키 삭제
        response.delete_cookie("access_token", path="/")
        response.delete_cookie("refresh_token", path="/auth")