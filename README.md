# NotoDo

> FastAPI 기반 Notion 할 일 연동 REST API + React(TypeScript) SPA

## 🧩 Tech Stack

### Backend
- **Language**: Python 3.11
- **Framework**: FastAPI
- **Server**: Uvicorn (ASGI)
- **Validation**: Pydantic
- **Authentication**: OAuth2 Bearer Token (JWT)
- **API**: RESTful API

### Frontend
- **Framework**: React
- **Language**: TypeScript
- **Build Tool**: Vite
- **Compiler**: SWC
- **Tooling**: ESLint, Prettier

### Database
- MongoDB

## TODO
- [X] 프로젝트 Init
- [X] 프론트엔드 프로젝트 생성(React + Vite + TypeScript + SWC)
- [X] TODOList / TODOForm(Create + Update) 화면 생성(Router)
- [ ] TODOForm 데이터 매칭 및 데이터 로컬 저장
- [ ] Login, Logout 구현 : Zustand 활용
- [ ] ⏸️ v0에서 생성한 디자인 적용(부트스트랩 활용 검토)
- [ ] 파이썬(FastAPI) 이용 - Todo 목록 CRUD 구현(연동X)
- [ ] Notion 연동 - 작업 목록 연동
- [ ] 인증 - JWT 이용
