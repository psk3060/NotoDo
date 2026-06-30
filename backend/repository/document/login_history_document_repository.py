class LoginHistoryDocumentRepository:
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