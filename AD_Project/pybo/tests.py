import os
from unittest.mock import patch

from django.contrib.auth.models import AnonymousUser, User
from django.test import SimpleTestCase, TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from config.settings import build_database_config
from .exceptions import AuthenticationRequiredError
from .models import Answer, Bookmark, Comment, Question
from .services import toggle_question_bookmark


class DatabaseConfigTests(SimpleTestCase):
    @patch.dict(os.environ, {}, clear=True)
    def test_sqlite_is_default_database(self):
        config = build_database_config()
        self.assertEqual(config['default']['ENGINE'], 'django.db.backends.sqlite3')

    @patch.dict(
        os.environ,
        {
            'DB_ENGINE': 'postgresql',
            'DB_NAME': 'pybo',
            'DB_USER': 'postgres',
            'DB_PASSWORD': 'password',
            'DB_HOST': 'localhost',
            'DB_PORT': '5432',
        },
        clear=True,
    )
    def test_postgresql_database_config_from_environment(self):
        config = build_database_config()
        self.assertEqual(config['default']['ENGINE'], 'django.db.backends.postgresql')
        self.assertEqual(config['default']['NAME'], 'pybo')
        self.assertEqual(config['default']['PORT'], '5432')


class PyboServiceApiTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='tester', password='password123', email='tester@example.com')
        self.other_user = User.objects.create_user(username='other', password='password123')
        self.question = Question.objects.create(
            author=self.user,
            subject='Django DRF service test',
            content='request response bookmark summary',
            create_date=timezone.now(),
        )
        self.answer = Answer.objects.create(
            author=self.other_user,
            question=self.question,
            content='answer content',
            create_date=timezone.now(),
        )
        Comment.objects.create(
            author=self.other_user,
            question=self.question,
            content='comment content',
            create_date=timezone.now(),
        )
        self.api_client = APIClient()

    def test_request_info_api_reads_request_message(self):
        response = self.api_client.get(
            '/api/request-info/?keyword=django&tag=a&tag=b',
            HTTP_USER_AGENT='AD-Test-Agent',
            REMOTE_ADDR='127.0.0.10',
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['method'], 'GET')
        self.assertEqual(response.data['path'], '/api/request-info/')
        self.assertEqual(response.data['query_params']['keyword'], 'django')
        self.assertEqual(response.data['query_params']['tag'], ['a', 'b'])
        self.assertEqual(response.data['user_agent'], 'AD-Test-Agent')

    def test_auth_api_login_me_logout(self):
        response = self.api_client.post(
            '/api/auth/login/',
            {'username': 'tester', 'password': 'password123'},
            format='json',
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['user']['username'], 'tester')

        response = self.api_client.get('/api/auth/me/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['user']['email'], 'tester@example.com')

        response = self.api_client.post('/api/auth/logout/')
        self.assertEqual(response.status_code, 200)

        response = self.api_client.get('/api/auth/me/')
        self.assertIn(response.status_code, (401, 403))

    def test_auth_api_rejects_invalid_credentials(self):
        response = self.api_client.post(
            '/api/auth/login/',
            {'username': 'tester', 'password': 'wrong'},
            format='json',
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['code'], 'invalid_credentials')

    def test_question_search_order_and_summary_api(self):
        second_question = Question.objects.create(
            author=self.other_user,
            subject='Unique search target',
            content='another content',
            create_date=timezone.now(),
        )
        second_question.voter.add(self.user)
        Bookmark.objects.create(user=self.user, question=second_question, create_date=timezone.now())

        response = self.api_client.get('/api/questions/?keyword=unique')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['subject'], 'Unique search target')

        response = self.api_client.get('/api/questions/?order=votes')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data[0]['id'], second_question.id)

        response = self.api_client.get('/api/board/summary/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['question_count'], 2)
        self.assertEqual(response.data['answer_count'], 1)
        self.assertEqual(response.data['comment_count'], 1)
        self.assertEqual(response.data['bookmark_count'], 1)
        self.assertGreaterEqual(len(response.data['popular_questions']), 1)

    def test_bookmark_api_requires_login_and_toggles_bookmark(self):
        response = self.api_client.post(f'/api/questions/{self.question.id}/bookmark/')
        self.assertIn(response.status_code, (401, 403))

        self.api_client.force_authenticate(user=self.user)
        response = self.api_client.post(f'/api/questions/{self.question.id}/bookmark/')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data['bookmarked'])
        self.assertEqual(response.data['bookmark_count'], 1)

        response = self.api_client.get('/api/bookmarks/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

        response = self.api_client.post(f'/api/questions/{self.question.id}/bookmark/')
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.data['bookmarked'])
        self.assertEqual(response.data['bookmark_count'], 0)

    def test_service_raises_for_anonymous_bookmark_user(self):
        with self.assertRaises(AuthenticationRequiredError):
            toggle_question_bookmark(AnonymousUser(), self.question.id)

    def test_bookmark_html_ui_toggle_and_list(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse('pybo:detail', args=[self.question.id]))
        self.assertContains(response, '북마크 0')
        self.assertContains(response, '저장')

        response = self.client.get(reverse('pybo:bookmark_question', args=[self.question.id]))
        self.assertRedirects(response, reverse('pybo:detail', args=[self.question.id]))
        self.assertTrue(Bookmark.objects.filter(user=self.user, question=self.question).exists())

        response = self.client.get(reverse('pybo:bookmark_list'))
        self.assertContains(response, '내 북마크')
        self.assertContains(response, self.question.subject)
