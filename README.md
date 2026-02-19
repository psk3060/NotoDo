# NotoDo

> FastAPI 기반 Notion 할 일 연동 REST API + React(TypeScript) SPA

## 🧩 Tech Stack

### Backend
- **Language**: Python 3.11
- **Framework**: FastAPI, Beanie, SQLAlchemy
- **Server**: Uvicorn (ASGI)
- **Validation**: Pydantic
- **Authentication**: JWT Access/Refresh(Refresh Token Rotation + Redis 저장 + 토큰 갱신 이력 Trace)
- **API**: RESTful API

### Frontend
- **Framework**: React
- **Language**: TypeScript
- **Build Tool**: Vite
- **Compiler**: SWC
- **Tooling**: ESLint, Prettier

### Database(Docker에서 실행)
- PostgreSQL(SQLAlchemy) : 사용자, 사용자 보안 정책(토큰 정책)
- Redis : IP(접근 권한), Refresh Token(Refresh Token Active)
- MongoDB(Beanie) : Refresh Token 발급 이력, 로그인 시도 이력(성공 / 실패), 기능 접근 이력(성공 / 실패)

## TODO
- [X] 프로젝트 Init
- [X] 프론트엔드 프로젝트 생성(React + Vite + TypeScript + SWC)
- [X] TODOList / TODOForm(Create + Update) 화면 생성(Router)
- [X] TODOForm 데이터 매칭 및 데이터 로컬 저장 : Zustand 활용
- [X] Login, Logout 구현 : Zustand 활용
- [X] 서버 연동 : 파이썬(FastAPI) Todo 목록 CRUD 구현(Mock)
- [X] 서버 연동 : 비밀번호 암복호화(RSA)
- [X] 서버 연동 : 비밀번호 하이브리드 암복호화(RSA + AES)
- [X] 서버 연동 : 사용자 인증 JWT 이용(Redis 연동)
- [X] 프론트엔드 : 리팩토링(프론트엔드 완료)
- [X] 서버 DB 변경 : PostgreSQL으로 DB 마이그레이션
- [X] 서버 연동 : Access Token 재발급 로깅(MongoDB), IP 체크(Redis)
- [ ] Notion 연동 : 작업 목록 연동 CRUD(Internal Integration Authorization)
- [ ] Notion 연동 : 댓글 기능 추가
- [ ] Notion 연동 : 필터링(상태별, 날짜별, 제목 + 내용 검색) 추가
- [ ] 서버 연동 : 자주 사용하는 필터링 조건 저장
- [ ] Notion 연동 : 반복 작업 자동화
- [ ] Notion 연동 : 동기화
- [ ] Notion 연동 : 통계 대시보드
- [ ] Notion 연동 : 오프라인 모드
- [ ] ⏸️ Notion 연동 : OAUTH2 인증(public 통합 설정 필요하지만, 회사 관련 사항 입력 필수)
- [ ] ⏸️ Notion 연동 : WebSocket 연동하여 노션 변경사항 실시간 반영(웹훅은 SSL 활성화 URL 필요)
- [ ] ⏸️ v0에서 생성한 디자인 적용(부트스트랩 활용 검토)
