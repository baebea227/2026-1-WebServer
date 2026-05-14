# [과제 5] 스켈러튼 코드 — 학생용 시작 자료

> 📚 **웹서버컴퓨팅** · 김상철 교수 · 국민대학교 소프트웨어학부

---

## 📦 이 자료에 들어 있는 것

```
과제5_스켈러튼/
├── README.md                                       ← 이 파일 (설치/작성 가이드)
├── requirements.txt                                ← 필요 패키지 (Django)
├── shell_demo.py                                   ← Django shell 데모 (빈칸 있음, 작성 필요)
└── books/
    ├── __init__.py
    ├── models.py                                   ← 메인 작성 파일 (빈칸 있음, 작성 필요)
    └── management/
        ├── __init__.py
        └── commands/
            ├── __init__.py
            └── seed_books.py                       ← 샘플 데이터 등록 (완성 — 수정 X)
```

| 파일 | 학생이 작성? | 배점 |
|---|---|---|
| `books/models.py` | **✅ 작성 필요** | 12점 |
| `shell_demo.py` | **✅ 작성 필요** | 4점 |
| `seed_books.py` | ❌ 그대로 사용 | — |
| 출력 캡처 (별도 제출) | **✅ 4개 캡처** | 4점 |
| **합계** | | **20점** |

---

## 🚀 작업 순서

### 1단계 — 환경 준비

```bash
# (선택) 가상환경 생성
python -m venv venv
source venv/bin/activate            # macOS / Linux
# venv\Scripts\activate              # Windows

# Django 설치
pip install -r requirements.txt
```

### 2단계 — Django 프로젝트 생성

```bash
django-admin startproject mylibrary
cd mylibrary
python manage.py startapp books
```

### 3단계 — 스켈러튼 파일 배치

이 zip 안의 `books/` 폴더 내용을 방금 생성한 `mylibrary/books/` 폴더에 **덮어쓰기**합니다.
배치 후 구조는 다음과 같아야 합니다.

```
mylibrary/
├── manage.py
├── shell_demo.py                                   ← zip 의 shell_demo.py 를 여기로
├── mylibrary/
│   ├── __init__.py
│   ├── settings.py                                 ← 4단계에서 수정
│   └── ...
└── books/
    ├── __init__.py
    ├── apps.py                                     ← startapp 으로 자동 생성된 그대로 둠
    ├── admin.py
    ├── models.py                                   ← zip 파일로 교체 (빈칸 작성 필요)
    ├── views.py
    ├── tests.py
    └── management/
        ├── __init__.py
        └── commands/
            ├── __init__.py
            └── seed_books.py
```

### 4단계 — `settings.py` 수정

`mylibrary/settings.py` 의 `INSTALLED_APPS` 에 `'books'` 를 추가합니다.

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'books',                # ← 추가
]
```

### 5단계 — `books/models.py` 빈칸 채우기 ✏️ (12점)

`books/models.py` 를 열어 `▼ TODO` 주석이 있는 8 곳을 채웁니다. 각 빈칸 옆에 배점이 있습니다.

### 6단계 — 마이그레이션 & 시드 데이터 등록

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py seed_books        # 책 3권 등록
```

> ⚠️ `seed_books` 명령을 두 번 이상 실행하면 같은 책이 중복 등록됩니다.
> 다시 등록하려면 `db.sqlite3` 파일을 지우고 마이그레이션부터 다시 하세요.

### 7단계 — `shell_demo.py` 빈칸 채우기 ✏️ (4점)

`shell_demo.py` 를 열어 4개 `for` 루프의 빈칸을 채웁니다.

### 8단계 — 실행 & 출력 캡처 📷 (4점)

```bash
python manage.py shell
```

shell 이 열리면 `shell_demo.py` 의 코드를 한 줄씩 복사해서 입력합니다. 4개 출력 영역(📚, ✍️, 🔍, 🔠)을 **각각 캡처**해 둡니다.

> 또는 한 번에 실행하기:
> ```bash
> python manage.py shell < shell_demo.py
> ```

---

## ✅ 정상 출력 (이 결과가 나와야 만점)

```
📚 전체 책 목록:
1984 by George Orwell
Brave New World by Aldous Huxley
Fahrenheit 451 by Ray Bradbury

✍️ George Orwell 책 목록:
1984 by George Orwell

🔍 제목에 'new'가 포함된 책 목록:
Brave New World by Aldous Huxley

🔠 제목순 정렬:
1984 by George Orwell
Brave New World by Aldous Huxley
Fahrenheit 451 by Ray Bradbury
```

---

## 📤 제출 안내 (반드시 준수)

| 항목 | 내용 |
|---|---|
| **파일 형식** | PDF 1개 파일로 통합 제출 |
| **파일명** | `학번_이름.pdf` (예: `20231234_홍길동.pdf`) |
| **PDF 구성** | [문제1] models.py → [문제2] shell 스크립트 → [문제3] 출력 캡처 4개 순서 |
| **GitHub / Notion 링크** | 활용 시 캡처 1장 + URL 함께 기재 (반드시 **Public** 설정) |

> 🚨 **반드시 확인하세요**
>
> GitHub 저장소 / Notion 페이지가 **Private** 상태이면 채점자가 접근할 수 없어 해당 항목 평가가 불가능합니다. 반드시 **Public** 으로 변경 후 제출하세요.

### ⚠️ 이전 과제에서 자주 발생한 실수

- Notion 페이지 Public 설정 누락
- `seed_books.py` 코드를 임의로 줄여 책 1권만 등록
- PDF 가 아닌 `.docx` / `.hwp` / `.zip` 형식으로 제출
- 파일명을 `과제5.pdf`, `숙제.pdf` 등으로 제출

---

## 💡 자주 묻는 질문

**Q. `cls` 가 뭔가요?**
A. `@classmethod` 로 정의된 메서드의 첫 번째 인자입니다. `self` 가 인스턴스(객체)를 가리킨다면, `cls` 는 클래스 자체(`Book` 클래스)를 가리킵니다. `cls.objects.all()` 은 `Book.objects.all()` 과 같은 의미입니다.

**Q. `QuerySet['Book']` 에서 따옴표를 쓰는 이유는?**
A. 클래스 본문 안에서는 `Book` 클래스 정의가 아직 완료되지 않았기 때문에 직접 참조할 수 없습니다. 문자열로 감싸면 나중에 평가되는 **forward reference** 가 되어 정상 동작합니다.

**Q. `__iexact` 와 `__icontains` 의 차이는?**
A. 둘 다 'i' 접두사는 **case-insensitive** (대소문자 구분 안 함) 를 의미합니다.
- `__iexact` : **정확 일치** (전체가 같아야 함)
- `__icontains` : **부분 일치** (포함만 되면 됨)

**Q. `seed_books` 를 실수로 두 번 실행했어요.**
A. 책이 6권으로 늘어납니다. 다음 중 하나로 해결:
1. `python manage.py shell` 에서 `Book.objects.all().delete()` 실행 후 다시 `python manage.py seed_books`
2. `mylibrary/db.sqlite3` 파일을 삭제하고 `python manage.py migrate` 부터 다시 실행

---

화이팅! 🚀
