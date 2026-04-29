"""
[과제 3] qa/management/commands/seed_data.py
TODO: 사용자 5명과 질문/답변을 자동 생성하는 management command를 완성하세요.
실행: python manage.py seed_data
"""
import random
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from qa.models import Question, Answer


class Command(BaseCommand):
    help = 'Create test users, questions, and answers'

    def handle(self, *args, **kwargs):
        # TODO: 사용자 5명 생성 (user1~user5, 비밀번호: test1234)
        for i in range(5):
            username = f'user{i+1}'
            if not User.objects.filter(username=username).exists():
                # TODO: User를 생성하세요
                # 힌트: User.objects.create_user(username=username, password='test1234')
                User.objects.create_user(username=username, password='test1234')
                self.stdout.write(f"Created user: {username}")

        users = list(User.objects.all())

        # 한국어 질문 데이터
        questions_data = [
            {
                'title': 'Django에서 모델 마이그레이션이 안 될 때 어떻게 하나요?',
                'content': 'makemigrations를 실행했는데 No changes detected라고 나옵니다. 해결 방법이 있을까요?',
                'answers': [
                    'python manage.py makemigrations 앱이름 으로 앱 이름을 명시적으로 지정해 보세요.',
                    'apps.py에서 앱 이름이 정확히 설정되어 있는지 확인해 보세요.',
                ],
            },
            {
                'title': 'Python 가상환경은 왜 사용하나요?',
                'content': '파이썬 프로젝트를 할 때 가상환경을 꼭 만들어야 하나요?',
                'answers': [
                    '프로젝트마다 필요한 패키지 버전이 다를 수 있어서 가상환경으로 분리하는 것이 좋습니다.',
                    '가상환경을 사용하면 프로젝트 간 패키지 충돌을 방지할 수 있습니다.',
                ],
            },
            {
                'title': 'Bootstrap 5를 사용하나요',
                'content': 'Bootstrap 5를 사용하나요',
                'answers': [
                    'CDN 링크를 HTML head에 추가하면 바로 사용할 수 있습니다.',
                ],
            },
            {
                'title': '장고 id는 자동으로 생성되나요?',
                'content': '장고 id는 자동으로 생성되나요?',
                'answers': [
                    '네, Django는 모델에 별도로 primary key를 지정하지 않으면 자동으로 id 필드를 생성합니다.',
                ],
            },
            {
                'title': 'pybo 질문',
                'content': 'pybo는 어떤 서비스인가요',
                'answers': [
                    'pybo는 점프 투 장고 교재에서 사용하는 Q&A 게시판 예제 프로젝트입니다.',
                ],
            },
            {
                'title': 'Git과 GitHub의 차이가 뭔가요?',
                'content': 'Git이랑 GitHub가 같은 건가요? 둘의 차이점을 알고 싶습니다.',
                'answers': [
                    'Git은 버전 관리 도구이고, GitHub는 Git 저장소를 호스팅하는 웹 서비스입니다.',
                ],
            },
            {
                'title': 'CSS Flexbox와 Grid 중 어떤 걸 써야 하나요?',
                'content': '레이아웃을 잡을 때 Flexbox와 Grid 중 어떤 것을 사용하는 것이 좋을까요?',
                'answers': [
                    '1차원 배치는 Flexbox, 2차원 배치는 Grid가 적합합니다.',
                    '둘 다 익혀두면 상황에 맞게 선택할 수 있어서 좋습니다.',
                ],
            },
            {
                'title': 'Django에서 로그아웃 시 405 에러가 발생합니다',
                'content': 'Logout 링크를 클릭하면 405 Method Not Allowed 에러가 납니다.',
                'answers': [
                    'Django의 LogoutView는 POST 방식만 허용합니다. form method="post"를 사용하세요.',
                ],
            },
            {
                'title': 'SQLite와 PostgreSQL 중 어떤 것을 사용해야 하나요?',
                'content': '개인 프로젝트에서 어떤 DB를 선택해야 하나요?',
                'answers': [
                    '개발 단계에서는 SQLite가 간편하고, 배포 시에는 PostgreSQL을 추천합니다.',
                ],
            },
            {
                'title': 'REST API란 무엇인가요?',
                'content': 'REST API가 정확히 뭔지 쉽게 설명해 주실 수 있나요?',
                'answers': [
                    'REST API는 HTTP 메서드를 사용하여 리소스를 다루는 웹 API 설계 방식입니다.',
                    'Django에서는 Django REST Framework를 사용하면 쉽게 만들 수 있습니다.',
                ],
            },
        ]

        for qdata in questions_data:
            author = random.choice(users)
            # TODO: Question 객체를 생성하세요
            # 힌트: Question.objects.create(title=..., content=..., author=...)
            q = Question.objects.create(title=qdata['title'], content=qdata['content'], author=author)
            self.stdout.write(f"Created question: {q.title}")

            for ans_content in qdata['answers']:
                # TODO: Answer 객체를 생성하세요
                # 힌트: Answer.objects.create(question=q, content=..., author=...)
                Answer.objects.create(question=q, content=ans_content, author=random.choice(users))
                self.stdout.write(f"  -> Added answer")
