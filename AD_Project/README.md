# AD_Project

`AD_Project`는 점프 투 장고 교재의 `pybo` 게시판을 기반으로 신규 기능 7개를 확장한 Django 웹 애플리케이션입니다.

기본 코드는 [`pahkey/djangobook`의 `3-12` 브랜치](https://github.com/pahkey/djangobook/tree/3-12)를 기준으로 하며, 기존 질문/답변 게시판 기능에 REST API, 북마크, 통계, 검색/정렬, PostgreSQL 환경 설정 등을 추가했습니다.

## 주요 기능

### 교재 기본 기능

- 회원가입, 로그인, 로그아웃
- 질문 목록, 질문 상세 조회
- 질문 등록, 수정, 삭제
- 답변 등록, 수정, 삭제
- 댓글 등록, 수정, 삭제
- 질문/답변 추천

### 신규 기능 7개

1. Request 정보 확인 API
   - Django request 객체에서 `method`, `path`, `query_params`, `user_agent`, `client_ip`를 읽어 JSON 응답으로 반환합니다.

2. Auth API
   - `django.contrib.auth.authenticate`, `login`, `logout`을 사용해 API 기반 로그인, 로그아웃, 내 정보 확인을 제공합니다.

3. 질문 북마크 API/UI
   - 질문을 저장하거나 저장 해제할 수 있습니다.
   - 내 북마크 목록 화면을 제공합니다.
   - 동일 사용자의 중복 북마크를 방지합니다.
   - 로그인하지 않은 사용자의 북마크 요청은 인증 예외로 처리합니다.

4. 게시판 통계 API
   - 질문 수, 답변 수, 댓글 수, 추천 수, 북마크 수를 반환합니다.
   - 추천 수, 북마크 수, 작성일 기준으로 인기 질문을 반환합니다.
   - classmethod 기반 DTO를 사용해 응답 데이터를 구성합니다.

5. 질문 검색/정렬 API
   - 키워드로 질문 제목, 내용, 작성자, 답변 내용을 검색합니다.
   - 최신순, 추천순, 답변순, 북마크순 정렬을 지원합니다.

6. 스크롤 초기화
   - 상세 페이지 이동, 답변 등록, 추천 이후 브라우저의 이전 스크롤 위치가 어색하게 남지 않도록 스크롤 복원 동작을 조정합니다.
   - 필요한 경우 앵커 이동을 활용해 사용자가 기대하는 위치로 이동합니다.

7. PostgreSQL 적용
   - WikiDocs의 PostgreSQL 적용 방식처럼 DB 접속 정보를 환경변수로 분리했습니다.
   - 로컬 실행 안정성을 위해 환경변수가 없으면 SQLite를 기본값으로 사용합니다.

## 기술 스택

- Python
- Django 5.2
- Django REST Framework
- SQLite
- PostgreSQL
- Bootstrap
- jQuery

## 프로젝트 구조

```text
AD_Project/
├── common/          # 회원가입 및 인증 관련 앱
├── config/          # Django 프로젝트 설정
├── pybo/            # 게시판 도메인, 화면, API, 서비스 로직
├── static/          # CSS, JavaScript 정적 파일
├── templates/       # 공통 및 앱별 HTML 템플릿
├── manage.py
├── requirements.txt
└── .env.example
```

## 실행 방법

### 1. 가상환경 생성 및 활성화

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 2. 의존성 설치

```powershell
pip install -r requirements.txt
```

### 3. 환경변수 설정

SQLite를 사용할 경우 별도 설정 없이 실행할 수 있습니다.

PostgreSQL을 사용할 경우 `.env.example`을 참고해 `.env` 파일을 생성합니다.

```env
DB_ENGINE=postgresql
DB_NAME=pybo
DB_USER=postgres
DB_PASSWORD=change-me
DB_HOST=localhost
DB_PORT=5432
```

`DB_ENGINE`이 `postgresql`이거나 PostgreSQL 접속 정보가 모두 설정되어 있으면 PostgreSQL을 사용합니다. 환경변수가 없으면 `db.sqlite3`를 사용하는 SQLite 설정으로 동작합니다.

### 4. 데이터베이스 마이그레이션

```powershell
python manage.py migrate
```

### 5. 관리자 계정 생성

```powershell
python manage.py createsuperuser
```

### 6. 개발 서버 실행

```powershell
python manage.py runserver
```

브라우저에서 다음 주소로 접속합니다.

```text
http://127.0.0.1:8000/
```

## 주요 화면 URL

| URL | 설명 |
| --- | --- |
| `/` | 질문 목록 메인 화면 |
| `/pybo/` | 질문 목록 |
| `/pybo/<question_id>/` | 질문 상세 |
| `/pybo/bookmark/` | 내 북마크 목록 |
| `/common/login/` | 로그인 |
| `/common/signup/` | 회원가입 |
| `/admin/` | Django 관리자 |

## 주요 API URL

| Method | URL | 설명 | 인증 |
| --- | --- | --- | --- |
| GET | `/api/request-info/` | 요청 정보 확인 | 불필요 |
| POST | `/api/auth/login/` | 로그인 | 불필요 |
| POST | `/api/auth/logout/` | 로그아웃 | 필요 |
| GET | `/api/auth/me/` | 내 정보 확인 | 필요 |
| GET | `/api/questions/?keyword=&order=` | 질문 검색/정렬 | 불필요 |
| POST | `/api/questions/<question_id>/bookmark/` | 질문 북마크 저장/해제 | 필요 |
| GET | `/api/bookmarks/` | 내 북마크 목록 | 필요 |
| GET | `/api/board/summary/` | 게시판 통계 | 불필요 |

### 질문 정렬 옵션

`/api/questions/`의 `order` query parameter는 다음 값을 지원합니다.

| 값 | 설명 |
| --- | --- |
| `recent` | 최신순 |
| `votes` | 추천순 |
| `answers` | 답변순 |
| `bookmarks` | 북마크순 |

예시:

```text
GET /api/questions/?keyword=django&order=votes
```

## 검증 및 테스트

### 자동 검증

다음 명령으로 Django 프로젝트 설정과 앱 구성을 먼저 점검합니다.

```powershell
python manage.py check
```

다음 명령으로 Django 테스트를 실행합니다.

```powershell
python manage.py test
```

`python manage.py check`는 Django 설정, 앱 등록, URL 구성, 모델 설정 등에 문제가 없는지 시스템 체크를 수행합니다.

테스트에는 DB 설정, Request 정보 API, Auth API, 질문 검색/정렬 API, 게시판 통계 API, 북마크 API/UI 동작 검증이 포함되어 있습니다.

### 수동 테스트

개발 서버를 실행한 뒤 브라우저와 API 클라이언트로 주요 기능을 직접 확인할 수 있습니다.

```powershell
python manage.py runserver
```

브라우저에서 `http://127.0.0.1:8000/`에 접속한 뒤 신규 기능 7개 순서대로 다음 시나리오를 확인합니다.

1. Request 정보 확인 API
   - `/api/request-info/?keyword=django&tag=a&tag=b`에 접속해 `method`, `path`, `query_params`, `user_agent`, `client_ip`가 JSON으로 반환되는지 확인합니다.

2. Auth API
   - `/api/auth/login/`에 `username`, `password`를 POST로 전달해 로그인되는지 확인합니다.
   - 로그인 후 `/api/auth/me/`에서 현재 사용자 정보가 반환되는지 확인합니다.
   - `/api/auth/logout/` 호출 후 다시 `/api/auth/me/`에 접근했을 때 인증이 필요한 응답이 나오는지 확인합니다.

3. 질문 북마크 API/UI
   - 로그인한 상태에서 질문 상세 화면의 북마크 버튼으로 저장/해제를 확인합니다.
   - `/pybo/bookmark/`에서 내 북마크 목록이 갱신되는지 확인합니다.
   - `/api/questions/<question_id>/bookmark/`를 반복 호출했을 때 중복 생성 없이 저장/해제가 토글되는지 확인합니다.

4. 게시판 통계 API
   - `/api/board/summary/`에 접속해 질문/답변/댓글/추천/북마크 수가 JSON으로 반환되는지 확인합니다.
   - `popular_questions`에 인기 질문 목록이 포함되는지 확인합니다.

5. 질문 검색/정렬 API
   - `/api/questions/?keyword=django`로 키워드 검색 결과를 확인합니다.
   - `/api/questions/?order=recent`, `/api/questions/?order=votes`, `/api/questions/?order=answers`, `/api/questions/?order=bookmarks`로 정렬 결과를 확인합니다.

6. 스크롤 초기화
   - 질문 상세 화면에서 아래쪽으로 스크롤한 뒤 목록으로 이동했다가 다시 상세 화면에 진입했을 때 어색한 이전 위치가 남지 않는지 확인합니다.
   - 답변 등록 또는 추천 후 화면 위치가 의도한 위치로 이동하는지 확인합니다.

7. PostgreSQL 적용
   - SQLite 환경에서는 `.env` 없이 서버가 실행되는지 확인합니다.
   - PostgreSQL 사용 시 `.env.example`을 참고해 `.env`를 작성한 뒤 `python manage.py check`와 `python manage.py migrate`가 정상 동작하는지 확인합니다.

## 참고

- 기본 코드: [pahkey/djangobook 3-12](https://github.com/pahkey/djangobook/tree/3-12)
- 교재: [점프 투 장고](https://wikidocs.net/book/4223)
