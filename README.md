# NotoDo

> FastAPI 기반 Notion 할 일 연동 REST API + React(TypeScript) SPA<br />
> Primary DB 기반 아키텍처로 확장 예정 (Notion은 외부 Sync 대상으로 활용)

## 📌 Project Overview
<p>NotoDo는 Notion과 연동되는 TODO 관리 시스템</p>
<p>초기에는 Notion을 Primary 데이터 소스로 설계하였으나, 성능 개선과 아키텍처 실험을 위해 다음과 같은 구조로 전환 예정</p>
<table>
  <thead>
    <tr>
      <th>단계</th>
      <th>Primary</th>
      <th>Secondary(Sync Target)</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Before</td>
      <td>Notion</td>
      <td>-</td>
    </tr>
    <tr>
      <td>After</td>
      <td>PostgreSQL</td>
      <td>Notion</td>
    </tr>
  </tbody>
</table>

****

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

### Database(Docker)
- PostgreSQL(SQLAlchemy) :
    - 사용자
    - 사용자 보안 정책(토큰 정책)
    - (Planned) TODO Primary 저장소
- Redis
    - IP(접근 권한)
    - Refresh Token(Refresh Token Active)
- MongoDB(Beanie)
    - Refresh Token 발급 이력
    - 로그인 시도 이력(성공 / 실패)
    - 기능 접근 이력(성공 / 실패)

***

## 🛠 Roadmap

### ✅ Completed
- 프로젝트 초기 세팅
- 프론트엔드 프로젝트 생성(React + Vite + TypeScript + SWC)
- TODOList / TODOForm(Create + Update) 화면 생성(Router)
- TODOForm 데이터 매칭 및 데이터 로컬 저장 : Zustand 활용
- 서버 연동 : 파이썬(FastAPI) Todo 목록 CRUD 구현(Mock)
- 서버 연동 : 비밀번호 암복호화(RSA). (고도화) 비밀번호 하이브리드 암복호화(RSA + AES)
- 서버 연동 : 사용자 JWT 인증(Redis 연동)
- 프론트엔드 : 리팩토링(프론트엔드 완료)
- 서버 DB 변경 : PostgreSQL으로 DB 마이그레이션
- 서버 연동 : Access Token 재발급 로깅(MongoDB), IP 체크(Redis)
- Notion 연동 : 작업 목록 연동 CRUD(Internal Integration Authorization)
- Notion 연동 : 댓글 기능(읽기, 쓰기)
- Notion 연동 : 필터링(상태별, 우선순위별, 제목 + 내용 검색) 추가, List 페이징

### 🔄 In Progress (Architecture Upgrade)
- [ ] Notion : Primary → Secondary(Sync), DB를 Primary로 (PostgreSQL 중심 구조)
- [ ] 서버 연동 : 자주 사용하는 필터링 조건 저장

### 🔮 고도화
- [ ] Notion 연동 : 통계 대시보드
- [ ] Notion 연동 : 오프라인 모드
- [ ] 메시지 큐 기반 동기화 설계

### ⏸️ On Hold (중단 항목)
- Notion 연동 : OAUTH2 인증
  - public 통합 설정 필요하지만, 회사 관련 사항 입력 필수
- Notion 연동 : WebSocket 연동하여 노션 변경사항 실시간 반영
  - 웹훅은 SSL 활성화 URL 필요
- v0에서 생성한 디자인 적용
  - 부트스트랩 활용
- Notion 연동 : 사용자 정보와 연동(Notion User_Id)
  - 다른 계정으로 로그인하여, 공용 영역에 작성 및 수정해보았으나 created_by와 last_edited_by 모두 동일(해당 기능 의미 없음)
