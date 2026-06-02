from django.contrib.auth.models import User
from django.db.models import ProtectedError
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Category, Question


class BookmarkViewsTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='user', password='password')
        self.other_user = User.objects.create_user(username='other', password='password')
        self.category = Category.objects.get(slug='qna')
        self.question = Question.objects.create(
            category=self.category,
            author=self.other_user,
            subject='bookmark subject',
            content='bookmark content',
            create_date=timezone.now(),
        )

    def test_bookmark_requires_login(self):
        url = reverse('pybo:bookmark_question', args=[self.question.id])

        response = self.client.get(url)

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('common:login'), response.url)

    def test_bookmark_question_toggles_current_user(self):
        self.client.login(username='user', password='password')
        url = reverse('pybo:bookmark_question', args=[self.question.id])

        self.client.get(url)
        self.assertTrue(self.question.bookmark.filter(id=self.user.id).exists())

        self.client.get(url)
        self.assertFalse(self.question.bookmark.filter(id=self.user.id).exists())

    def test_bookmark_list_shows_only_current_user_bookmarks(self):
        other_question = Question.objects.create(
            category=self.category,
            author=self.other_user,
            subject='not bookmarked subject',
            content='not bookmarked content',
            create_date=timezone.now(),
        )
        self.question.bookmark.add(self.user)
        other_question.bookmark.add(self.other_user)
        self.client.login(username='user', password='password')

        response = self.client.get(reverse('pybo:bookmark_list'))

        self.assertContains(response, self.question.subject)
        self.assertNotContains(response, other_question.subject)


class CategoryViewsTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='user', password='password')
        self.qna = Category.objects.get(slug='qna')
        self.lecture = Category.objects.get(slug='lecture')
        self.free = Category.objects.get(slug='free')
        self.qna_question = Question.objects.create(
            category=self.qna,
            author=self.user,
            subject='qna subject',
            content='common keyword',
            create_date=timezone.now(),
        )
        self.lecture_question = Question.objects.create(
            category=self.lecture,
            author=self.user,
            subject='lecture subject',
            content='common keyword',
            create_date=timezone.now(),
        )

    def test_default_categories_exist(self):
        categories = set(Category.objects.values_list('slug', 'name'))

        self.assertEqual(
            categories,
            {('qna', '질문답변'), ('lecture', '강좌'), ('free', '자유게시판')},
        )

    def test_index_filters_by_category(self):
        response = self.client.get(reverse('pybo:index'), {'category': 'lecture'})

        self.assertContains(response, self.lecture_question.subject)
        self.assertNotContains(response, self.qna_question.subject)

    def test_index_filters_by_category_and_keyword(self):
        hidden_question = Question.objects.create(
            category=self.lecture,
            author=self.user,
            subject='hidden subject',
            content='other content',
            create_date=timezone.now(),
        )

        response = self.client.get(
            reverse('pybo:index'),
            {'category': 'lecture', 'kw': 'common'},
        )

        self.assertContains(response, self.lecture_question.subject)
        self.assertNotContains(response, self.qna_question.subject)
        self.assertNotContains(response, hidden_question.subject)

    def test_question_create_saves_category(self):
        self.client.login(username='user', password='password')

        response = self.client.post(reverse('pybo:question_create'), {
            'category': self.free.id,
            'subject': 'free subject',
            'content': 'free content',
        })

        self.assertEqual(response.status_code, 302)
        question = Question.objects.get(subject='free subject')
        self.assertEqual(question.category, self.free)

    def test_question_modify_updates_category(self):
        self.client.login(username='user', password='password')

        response = self.client.post(
            reverse('pybo:question_modify', args=[self.qna_question.id]),
            {
                'category': self.free.id,
                'subject': self.qna_question.subject,
                'content': self.qna_question.content,
            },
        )

        self.assertEqual(response.status_code, 302)
        self.qna_question.refresh_from_db()
        self.assertEqual(self.qna_question.category, self.free)

    def test_category_with_question_is_protected(self):
        with self.assertRaises(ProtectedError):
            self.qna.delete()
