import os, jwt, json

def decodeAccessToken(access_token : str, decoding_token_type : str | None = 'jwt') -> str:
    
        SECRET_KEY = os.getenv('ACCESS_TOKEN_SECRET_KEY')
        TOKEN_ALGORITHM = os.getenv('TOKEN_ALGORITHM') 
        TOKEN_ISSUER = os.getenv('TOKEN_ISSUER', 'localhost')
        
        try:
            
            if not SECRET_KEY or SECRET_KEY == '':
                raise Exception("SECRET_KEY가 설정되지 않았습니다.")
            
            if not TOKEN_ALGORITHM or TOKEN_ALGORITHM == '':
                raise Exception("토큰 알고리즘이 설정되지 않았습니다.")
            
            if decoding_token_type == 'jwt':
                payload = jwt.decode(access_token, SECRET_KEY, algorithms=[TOKEN_ALGORITHM], issuer = TOKEN_ISSUER)
    
            payload["code"] = "success"
            payload["message"] = "토큰이 정상적으로 인코딩 되었습니다."
            
            return json.dumps(payload)
        
        except Exception as e:
            print(e)
            raise e