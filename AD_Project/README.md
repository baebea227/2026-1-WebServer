# AD Project - Pybo
  
[pahkey/djangobook pybo 3-12](https://github.com/pahkey/djangobook/tree/3-12) 기반 프로젝트입니다.
## 주요 기능

### 신규 서비스 5개

| 기능 | 설명 |
| --- | --- |
| 인기 질문 | 조회수, 추천 수, 댓글 수를 합산한 점수 기준으로 인기 질문 목록 제공 |
| 북마크 | 로그인 사용자가 관심 질문을 북마크하고 북마크 목록에서 확인 |
| 마이페이지 | 사용자가 작성한 질문, 답변, 댓글과 추천/북마크 활동을 한 화면에서 확인 |
| 신고/신고관리 | 질문, 답변, 댓글 신고 기능과 관리자용 신고 처리 기능 제공 |
| 알림 | 답변, 댓글, 추천 발생 시 대상 사용자에게 알림 생성 및 읽음 처리 |

### 교과서 선택 구현 서비스 2개

| 기능 | 설명 |
| --- | --- |
| 검색 | 질문 제목, 질문 내용, 답변 내용, 작성자 기준으로 게시글 검색 |
| 질문 유형 | 에러/버그, 개념/이론, 구현/코드, 환경설정, 기타 유형별 질문 분류 및 조회 |

## 기술 스택

- Python
- Django
- SQLite
- Bootstrap
- jQuery

## 프로젝트 구조

```text
AD_Project/
├── common/          # 로그인, 로그아웃, 회원가입 등 공통 사용자 기능
├── config/          # Django 프로젝트 설정 및 URL 설정
├── pybo/            # 게시판 모델, 폼, 뷰, URL, 테스트
├── static/          # Bootstrap, jQuery, 사용자 CSS
├── templates/       # 공통 템플릿과 pybo/common 화면 템플릿
├── db.sqlite3       # SQLite 데이터베이스
└── manage.py        # Django 관리 명령 실행 파일
```

## 실행 방법

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install django
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

서버 실행 후 브라우저에서 다음 주소로 접속합니다.

```text
http://127.0.0.1:8000/
```

관리자 페이지는 다음 주소에서 접속할 수 있습니다.

```text
http://127.0.0.1:8000/admin/
```

## 기본 질문 유형

마이그레이션 실행 시 다음 기본 질문 유형이 생성됩니다.

- 에러/버그 (`error`)
- 개념/이론 (`concept`)
- 구현/코드 (`implementation`)
- 환경설정 (`environment`)
- 기타 (`etc`)

## 검증 방법

프로젝트 상태 확인:

```powershell
python manage.py check
```

테스트 실행:

```powershell
python manage.py test
```

## 주요 URL

| URL | 설명 |
| --- | --- |
| `/` | 게시글 목록 |
| `/pybo/popular/` | 인기 질문 목록 |
| `/pybo/bookmark/` | 북마크 목록 |
| `/pybo/mypage/` | 마이페이지 |
| `/pybo/notifications/` | 알림 목록 |
| `/pybo/reports/` | 신고 관리 |
| `/common/login/` | 로그인 |
| `/common/signup/` | 회원가입 |
