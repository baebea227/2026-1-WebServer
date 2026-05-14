# 과제 3: 간단한 Q&A 사이트 개발하기 (스켈레톤 코드)

## 사용법

각 파일의 `______` (빈칸)을 채워서 프로젝트를 완성하세요.
각 파일 상단의 TODO 주석과 힌트를 참고하세요.

## 실행 순서

```bash
pip install django
python manage.py makemigrations qa
python manage.py migrate
python manage.py createsuperuser
python manage.py seed_data
python manage.py runserver 8020
```

## 접속
- http://127.0.0.1:8020/
- 로그인: user1 / test1234

## 빈칸 목록 (총 약 40개)
- settings.py: 3개
- qna_site/urls.py: 3개
- qa/models.py: 8개
- qa/admin.py: 2개
- qa/views.py: 10개
- qa/urls.py: 3개
- seed_data.py: 3개
- templates: 약 15개
