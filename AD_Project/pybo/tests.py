from django.contrib.auth.models import User
from django.db.models import ProtectedError
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Answer, Category, Comment, ContentReport, Notification, Question


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


class MypageViewsTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='user', password='password')
        self.other_user = User.objects.create_user(username='other', password='password')
        self.category = Category.objects.get(slug='qna')
        self.my_question = Question.objects.create(
            category=self.category,
            author=self.user,
            subject='my question subject',
            content='my question content',
            create_date=timezone.now(),
        )
        self.other_question = Question.objects.create(
            category=self.category,
            author=self.other_user,
            subject='other question subject',
            content='other question content',
            create_date=timezone.now(),
        )
        self.my_answer = Answer.objects.create(
            author=self.user,
            question=self.other_question,
            content='my answer content',
            create_date=timezone.now(),
        )
        self.other_answer = Answer.objects.create(
            author=self.other_user,
            question=self.my_question,
            content='other answer content',
            create_date=timezone.now(),
        )
        self.question_comment = Comment.objects.create(
            author=self.user,
            question=self.other_question,
            content='my question comment',
            create_date=timezone.now(),
        )
        self.answer_comment = Comment.objects.create(
            author=self.user,
            answer=self.other_answer,
            content='my answer comment',
            create_date=timezone.now(),
        )
        Comment.objects.create(
            author=self.other_user,
            question=self.my_question,
            content='other comment content',
            create_date=timezone.now(),
        )
        self.other_question.voter.add(self.user)
        self.other_answer.voter.add(self.user)
        self.other_question.bookmark.add(self.user)

    def test_mypage_requires_login(self):
        response = self.client.get(reverse('pybo:mypage'))

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('common:login'), response.url)

    def test_mypage_shows_only_current_user_activity(self):
        self.client.login(username='user', password='password')

        response = self.client.get(reverse('pybo:mypage'))

        self.assertContains(response, self.my_question.subject)
        self.assertContains(response, self.my_answer.content)
        self.assertContains(response, self.question_comment.content)
        self.assertContains(response, self.answer_comment.content)
        self.assertContains(response, self.other_question.subject)
        self.assertContains(response, self.other_answer.content)
        self.assertNotContains(response, 'other comment content')

    def test_mypage_shows_empty_messages(self):
        User.objects.create_user(username='empty', password='password')
        self.client.login(username='empty', password='password')

        response = self.client.get(reverse('pybo:mypage'))

        self.assertContains(response, '작성한 질문이 없습니다.')
        self.assertContains(response, '작성한 답변이 없습니다.')
        self.assertContains(response, '작성한 댓글이 없습니다.')
        self.assertContains(response, '추천한 질문이 없습니다.')
        self.assertContains(response, '추천한 답변이 없습니다.')
        self.assertContains(response, '북마크한 질문이 없습니다.')


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


class ReportViewsTests(TestCase):
    def setUp(self):
        self.reporter = User.objects.create_user(username='reporter', password='password')
        self.author = User.objects.create_user(username='author', password='password')
        self.staff = User.objects.create_user(
            username='staff',
            password='password',
            is_staff=True,
        )
        self.category = Category.objects.get(slug='qna')
        self.question = Question.objects.create(
            category=self.category,
            author=self.author,
            subject='report subject',
            content='report content',
            create_date=timezone.now(),
        )

    def test_report_create_requires_login(self):
        url = reverse('pybo:report_create', args=['question', self.question.id])

        response = self.client.get(url)

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('common:login'), response.url)

    def test_report_create_saves_question_report(self):
        self.client.login(username='reporter', password='password')

        response = self.client.post(
            reverse('pybo:report_create', args=['question', self.question.id]),
            {
                'reason': 'inappropriate',
                'content': '부적절합니다.',
            },
        )

        self.assertEqual(response.status_code, 302)
        report = ContentReport.objects.get()
        self.assertEqual(report.reporter, self.reporter)
        self.assertEqual(report.question, self.question)
        self.assertEqual(report.status, 'pending')

    def test_report_create_blocks_duplicate_report(self):
        ContentReport.objects.create(
            reporter=self.reporter,
            question=self.question,
            reason='spam',
            create_date=timezone.now(),
        )
        self.client.login(username='reporter', password='password')

        self.client.post(
            reverse('pybo:report_create', args=['question', self.question.id]),
            {
                'reason': 'inappropriate',
                'content': '중복 신고',
            },
        )

        self.assertEqual(ContentReport.objects.count(), 1)

    def test_report_list_requires_staff(self):
        self.client.login(username='reporter', password='password')

        response = self.client.get(reverse('pybo:report_list'))

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('common:login'), response.url)

    def test_report_review_updates_status_by_staff(self):
        report = ContentReport.objects.create(
            reporter=self.reporter,
            question=self.question,
            reason='spam',
            create_date=timezone.now(),
        )
        self.client.login(username='staff', password='password')

        response = self.client.post(
            reverse('pybo:report_detail', args=[report.id]),
            {
                'status': 'resolved',
                'review_memo': '처리했습니다.',
            },
        )

        self.assertEqual(response.status_code, 302)
        report.refresh_from_db()
        self.assertEqual(report.status, 'resolved')
        self.assertEqual(report.reviewed_by, self.staff)


class NotificationViewsTests(TestCase):
    def setUp(self):
        self.author = User.objects.create_user(username='author', password='password')
        self.actor = User.objects.create_user(username='actor', password='password')
        self.other_user = User.objects.create_user(username='other', password='password')
        self.category = Category.objects.get(slug='qna')
        self.question = Question.objects.create(
            category=self.category,
            author=self.author,
            subject='notification subject',
            content='notification content',
            create_date=timezone.now(),
        )

    def test_answer_create_sends_notification_to_question_author(self):
        self.client.login(username='actor', password='password')

        response = self.client.post(reverse('pybo:answer_create', args=[self.question.id]), {
            'content': 'new answer',
        })

        self.assertEqual(response.status_code, 302)
        notification = Notification.objects.get()
        self.assertEqual(notification.recipient, self.author)
        self.assertEqual(notification.actor, self.actor)
        self.assertEqual(notification.notification_type, 'answer')
        self.assertEqual(notification.question, self.question)
        self.assertEqual(notification.answer.content, 'new answer')

    def test_question_comment_create_sends_notification_to_question_author(self):
        self.client.login(username='actor', password='password')

        response = self.client.post(reverse('pybo:comment_create_question', args=[self.question.id]), {
            'content': 'question comment',
        })

        self.assertEqual(response.status_code, 302)
        notification = Notification.objects.get()
        self.assertEqual(notification.recipient, self.author)
        self.assertEqual(notification.notification_type, 'comment')
        self.assertEqual(notification.question, self.question)
        self.assertEqual(notification.comment.content, 'question comment')

    def test_answer_comment_create_sends_notification_to_answer_author(self):
        answer = Answer.objects.create(
            question=self.question,
            author=self.author,
            content='answer content',
            create_date=timezone.now(),
        )
        self.client.login(username='actor', password='password')

        response = self.client.post(reverse('pybo:comment_create_answer', args=[answer.id]), {
            'content': 'answer comment',
        })

        self.assertEqual(response.status_code, 302)
        notification = Notification.objects.get()
        self.assertEqual(notification.recipient, self.author)
        self.assertEqual(notification.notification_type, 'comment')
        self.assertEqual(notification.answer, answer)
        self.assertEqual(notification.comment.content, 'answer comment')

    def test_question_vote_sends_notification_to_question_author(self):
        self.client.login(username='actor', password='password')

        response = self.client.get(reverse('pybo:vote_question', args=[self.question.id]))

        self.assertEqual(response.status_code, 302)
        notification = Notification.objects.get()
        self.assertEqual(notification.recipient, self.author)
        self.assertEqual(notification.notification_type, 'question_vote')
        self.assertEqual(notification.question, self.question)

    def test_answer_vote_sends_notification_to_answer_author(self):
        answer = Answer.objects.create(
            question=self.question,
            author=self.author,
            content='answer content',
            create_date=timezone.now(),
        )
        self.client.login(username='actor', password='password')

        response = self.client.get(reverse('pybo:vote_answer', args=[answer.id]))

        self.assertEqual(response.status_code, 302)
        notification = Notification.objects.get()
        self.assertEqual(notification.recipient, self.author)
        self.assertEqual(notification.notification_type, 'answer_vote')
        self.assertEqual(notification.answer, answer)

    def test_own_action_does_not_create_notification(self):
        self.client.login(username='author', password='password')

        self.client.post(reverse('pybo:answer_create', args=[self.question.id]), {
            'content': 'own answer',
        })
        self.client.post(reverse('pybo:comment_create_question', args=[self.question.id]), {
            'content': 'own comment',
        })
        self.client.get(reverse('pybo:vote_question', args=[self.question.id]))

        self.assertEqual(Notification.objects.count(), 0)

    def test_repeated_vote_does_not_create_additional_notification(self):
        self.client.login(username='actor', password='password')
        url = reverse('pybo:vote_question', args=[self.question.id])

        self.client.get(url)
        self.client.get(url)

        self.assertEqual(Notification.objects.count(), 1)

    def test_notification_list_requires_login(self):
        response = self.client.get(reverse('pybo:notification_list'))

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('common:login'), response.url)

    def test_notification_list_shows_only_current_user_notifications(self):
        Notification.objects.create(
            recipient=self.author,
            actor=self.actor,
            notification_type='answer',
            question=self.question,
            message='author notification',
            create_date=timezone.now(),
        )
        Notification.objects.create(
            recipient=self.other_user,
            actor=self.actor,
            notification_type='answer',
            question=self.question,
            message='other notification',
            create_date=timezone.now(),
        )
        self.client.login(username='author', password='password')

        response = self.client.get(reverse('pybo:notification_list'))

        self.assertContains(response, 'author notification')
        self.assertNotContains(response, 'other notification')

    def test_notification_read_marks_notification_and_redirects_to_question(self):
        notification = Notification.objects.create(
            recipient=self.author,
            actor=self.actor,
            notification_type='comment',
            question=self.question,
            message='read notification',
            create_date=timezone.now(),
        )
        self.client.login(username='author', password='password')

        response = self.client.get(reverse('pybo:notification_read', args=[notification.id]))

        self.assertRedirects(response, reverse('pybo:detail', args=[self.question.id]))
        notification.refresh_from_db()
        self.assertIsNotNone(notification.read_date)
