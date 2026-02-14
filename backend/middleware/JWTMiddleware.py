from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import os, jwt, json
from service.impl import AuthServiceImpl

class JWTMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        
        authService = AuthServiceImpl()
        
        force_logout = False
        
        # /todos만 검사
        if not request.url.path.startswith("/todos"):
            return await call_next(request)

        user_id = request.headers.get("userId")
        
        if not user_id :
            return JSONResponse(status_code=400,content={"code" : "empty_id", "message" : "회원ID가 비어있습니다."})
        
        access_token = request.cookies.get("access_token")
        
        if not access_token :
            return JSONResponse(status_code=401,content={"code" : "empty_token", "message" : "토큰이 비어있습니다."})
        
        try :
            # 1. Token 검증(만료, 유효성, 기타 에러만 검증)
            json_data = json.loads(authService.decodeToken(access_token))

            token_type = json_data["type"]
            
            if token_type != "access":
                return JSONResponse(status_code=403,content={"code" : "wrong_token_type", "message" : f"'{token_type}' 토큰은 이 API에서 사용할 수 없습니다."})
            
            
            token_user_id = json_data["user_id"]
    
            # 2. Token의 userId와 Header의 userId 비교 : 일치할 경우, 정상. 일치하지 않을 경우 블랙리스트 처리(TODO)
            if user_id != token_user_id:
                return JSONResponse(status_code=403,content={"code" : "user_mismatch", "message" : "요청한 회원ID와 토큰의 사용자ID가 일치하지 않습니다.", "force_logout": True})

            request.state.user = json_data["user_id"]
            
        except jwt.ExpiredSignatureError as e:
            return JSONResponse(
                status_code=401,
                content={"code": "expired", "message": "토큰이 만료되었습니다.", "force_logout" : False}
            )
        except jwt.InvalidTokenError as e:
            return JSONResponse(
                status_code=401,
                content={"code": "invalid", "message": "유효하지 않은 토큰입니다.", "force_logout" : True}
            )
        except Exception as e:
            return JSONResponse(
                status_code=500,
                content={"code": "fail", "message": str(e) or "Service Error"}
            )
            
        
        response = await call_next(request)
        return response