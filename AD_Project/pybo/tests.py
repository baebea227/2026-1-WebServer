from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Question


class BookmarkViewsTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='user', password='password')
        self.other_user = User.objects.create_user(username='other', password='password')
        self.question = Question.objects.create(
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
