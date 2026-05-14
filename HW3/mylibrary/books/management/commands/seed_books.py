"""
=================================================================
[과제 5] books/management/commands/seed_books.py
샘플 데이터 등록 — 관리 커맨드
=================================================================

⚠️ 이 파일은 수정하지 마세요. 그대로 사용합니다.

📌 사용 방법
   python manage.py seed_books

⚠️ 주의 사항
   - 명령을 두 번 이상 실행하면 같은 데이터가 중복 등록됩니다.
   - 다시 등록하려면 db.sqlite3 를 삭제하고 마이그레이션부터 다시 진행하거나,
     shell 에서 Book.objects.all().delete() 로 비운 후 실행하세요.
"""

from django.core.management.base import BaseCommand
from books.models import Book


class Command(BaseCommand):
    help = 'Insert sample books'

    def handle(self, *args, **kwargs):
        Book.objects.create(title='1984', author='George Orwell')
        Book.objects.create(title='Brave New World', author='Aldous Huxley')
        Book.objects.create(title='Fahrenheit 451', author='Ray Bradbury')
        self.stdout.write(self.style.SUCCESS('Sample books inserted!'))
