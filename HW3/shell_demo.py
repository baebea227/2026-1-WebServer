"""
=================================================================
[과제 5] shell_demo.py — Django Shell 데모 스크립트
=================================================================

📌 실행 방법

  방법 ① 한 줄씩 직접 입력 (권장 — 출력 캡처 용이)
        python manage.py shell
        # 그리고 아래 코드를 한 줄씩 복사해서 입력

  방법 ② 파일 전체 한 번에 실행
        python manage.py shell < shell_demo.py

📊 [문제 2] 배점: 4점 (for 루프 4개 × 1점)
📊 [문제 3] 배점: 4점 (출력 결과 캡처 4개 × 1점)

⚠️ 빈칸 표시
   - "_____" → 변수 이름이 들어갈 자리
   - 모든 빈칸을 채운 뒤 위 명령으로 실행해 출력 결과를 캡처하세요.
"""

from books.models import Book

# ──────────────────────────────────────────────────────────────
# 1. 전체 책 조회
# ──────────────────────────────────────────────────────────────
all_books = Book.get_all_books()
print("📚 전체 책 목록:")
# ▼ TODO 2-1 (1점): for 루프를 작성하여 all_books 의 각 책을 print 하세요.
#     형식:   for ___변수___ in ___컬렉션___:
for book in all_books:
    print(book)

# ──────────────────────────────────────────────────────────────
# 2. 특정 저자 책만 조회
# ──────────────────────────────────────────────────────────────
orwell_books = Book.get_books_by_author("George Orwell")
print("\n✍️ George Orwell 책 목록:")
# ▼ TODO 2-2 (1점): for 루프를 작성하여 orwell_books 의 각 책을 print 하세요.
for book in orwell_books:
    print(book)

# ──────────────────────────────────────────────────────────────
# 3. 제목 키워드로 검색
# ──────────────────────────────────────────────────────────────
dystopia_books = Book.get_books_by_title_keyword("new")
print("\n🔍 제목에 'new'가 포함된 책 목록:")
# ▼ TODO 2-3 (1점): for 루프를 작성하여 dystopia_books 의 각 책을 print 하세요.
for book in dystopia_books:
    print(book)

# ──────────────────────────────────────────────────────────────
# 4. 제목순 정렬
# ──────────────────────────────────────────────────────────────
sorted_books = Book.get_books_ordered_by_title()
print("\n🔠 제목순 정렬:")
# ▼ TODO 2-4 (1점): for 루프를 작성하여 sorted_books 의 각 책을 print 하세요.
for book in sorted_books:
    print(book)

# ──────────────────────────────────────────────────────────────
# ✅ 정상 출력 예시 (참고용)
# ──────────────────────────────────────────────────────────────
#
# 📚 전체 책 목록:
# 1984 by George Orwell
# Brave New World by Aldous Huxley
# Fahrenheit 451 by Ray Bradbury
#
# ✍️ George Orwell 책 목록:
# 1984 by George Orwell
#
# 🔍 제목에 'new'가 포함된 책 목록:
# Brave New World by Aldous Huxley
#
# 🔠 제목순 정렬:
# 1984 by George Orwell
# Brave New World by Aldous Huxley
# Fahrenheit 451 by Ray Bradbury
