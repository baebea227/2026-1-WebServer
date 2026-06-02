from datetime import timedelta

from django.contrib.auth.models import User
from django.db import IntegrityError, transaction
from django.db.models import ProtectedError
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from .models import Answer, Category, Comment, ContentReport, Notification, Question


@override_settings(PASSWORD_HASHERS=['django.contrib.auth.hashers.MD5PasswordHasher'])
class FastPasswordTestCase(TestCase):
    pass


class BookmarkViewsTests(FastPasswordTestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='user', password='password')
        self.other_user = User.objects.create_user(username='other', password='password')
        self.category = Category.objects.get(slug='etc')
        self.question = Question.objects.create(
            category=self.category,
            author=self.other_user,
            subject='bookmark subject',
            content='bookmark content',
            create_date=timezone.now(),
        )

    def test_bookmark_requires_login(self):
        url = reverse('pybo:bookmark_question', args=[self.question.id])

        response = self.client.post(url)

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('common:login'), response.url)

    def test_bookmark_get_method_is_not_allowed(self):
        self.client.login(username='user', password='password')

        response = self.client.get(reverse('pybo:bookmark_question', args=[self.question.id]))

        self.assertEqual(response.status_code, 405)

    def test_bookmark_question_toggles_current_user(self):
        self.client.login(username='user', password='password')
        url = reverse('pybo:bookmark_question', args=[self.question.id])

        self.client.post(url)
        self.assertTrue(self.question.bookmark.filter(id=self.user.id).exists())

        self.client.post(url)
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


class MypageViewsTests(FastPasswordTestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='user', password='password')
        self.other_user = User.objects.create_user(username='other', password='password')
        self.category = Category.objects.get(slug='etc')
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


class CategoryViewsTests(FastPasswordTestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='user', password='password')
        self.error = Category.objects.get(slug='error')
        self.concept = Category.objects.get(slug='concept')
        self.environment = Category.objects.get(slug='environment')
        self.error_question = Question.objects.create(
            category=self.error,
            author=self.user,
            subject='error subject',
            content='common keyword',
            create_date=timezone.now(),
        )
        self.concept_question = Question.objects.create(
            category=self.concept,
            author=self.user,
            subject='concept subject',
            content='common keyword',
            create_date=timezone.now(),
        )

    def test_default_categories_exist(self):
        categories = set(Category.objects.values_list('slug', 'name'))

        self.assertEqual(
            categories,
            {
                ('error', '에러/버그'),
                ('concept', '개념/이론'),
                ('implementation', '구현/코드'),
                ('environment', '환경설정'),
                ('etc', '기타'),
            },
        )

    def test_index_filters_by_category(self):
        response = self.client.get(reverse('pybo:index'), {'category': 'concept'})

        self.assertContains(response, self.concept_question.subject)
        self.assertNotContains(response, self.error_question.subject)

    def test_index_filters_by_category_and_keyword(self):
        hidden_question = Question.objects.create(
            category=self.concept,
            author=self.user,
            subject='hidden subject',
            content='other content',
            create_date=timezone.now(),
        )

        response = self.client.get(
            reverse('pybo:index'),
            {'category': 'concept', 'kw': 'common'},
        )

        self.assertContains(response, self.concept_question.subject)
        self.assertNotContains(response, self.error_question.subject)
        self.assertNotContains(response, hidden_question.subject)

    def test_question_create_saves_category(self):
        self.client.login(username='user', password='password')

        response = self.client.post(reverse('pybo:question_create'), {
            'category': self.environment.id,
            'subject': 'environment subject',
            'content': 'environment content',
        })

        self.assertEqual(response.status_code, 302)
        question = Question.objects.get(subject='environment subject')
        self.assertEqual(question.category, self.environment)

    def test_question_modify_updates_category(self):
        self.client.login(username='user', password='password')

        response = self.client.post(
            reverse('pybo:question_modify', args=[self.error_question.id]),
            {
                'category': self.environment.id,
                'subject': self.error_question.subject,
                'content': self.error_question.content,
            },
        )

        self.assertEqual(response.status_code, 302)
        self.error_question.refresh_from_db()
        self.assertEqual(self.error_question.category, self.environment)

    def test_category_with_question_is_protected(self):
        with self.assertRaises(ProtectedError):
            self.error.delete()


class MutationMethodTests(FastPasswordTestCase):
    def setUp(self):
        self.author = User.objects.create_user(username='author', password='password')
        self.category = Category.objects.get(slug='etc')
        self.question = Question.objects.create(
            category=self.category,
            author=self.author,
            subject='delete subject',
            content='delete content',
            create_date=timezone.now(),
        )

    def test_question_delete_get_method_is_not_allowed(self):
        self.client.login(username='author', password='password')

        response = self.client.get(reverse('pybo:question_delete', args=[self.question.id]))

        self.assertEqual(response.status_code, 405)
        self.assertTrue(Question.objects.filter(id=self.question.id).exists())

    def test_question_delete_post_removes_question(self):
        self.client.login(username='author', password='password')

        response = self.client.post(reverse('pybo:question_delete', args=[self.question.id]))

        self.assertEqual(response.status_code, 302)
        self.assertFalse(Question.objects.filter(id=self.question.id).exists())


class PopularQuestionViewsTests(FastPasswordTestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='user', password='password')
        self.other_user = User.objects.create_user(username='other', password='password')
        self.category = Category.objects.get(slug='etc')

    def create_question(self, subject, view_count=0, create_date=None):
        return Question.objects.create(
            category=self.category,
            author=self.user,
            subject=subject,
            content=f'{subject} content',
            create_date=create_date or timezone.now(),
            view_count=view_count,
        )

    def test_question_view_count_defaults_to_zero(self):
        question = self.create_question('default view count')

        self.assertEqual(question.view_count, 0)

    def test_detail_increments_question_view_count(self):
        question = self.create_question('viewed question')

        response = self.client.get(reverse('pybo:detail', args=[question.id]))

        self.assertEqual(response.status_code, 200)
        question.refresh_from_db()
        self.assertEqual(question.view_count, 1)

    def test_detail_increments_view_count_once_per_session(self):
        question = self.create_question('session viewed question')
        url = reverse('pybo:detail', args=[question.id])

        self.client.get(url)
        self.client.get(url)

        question.refresh_from_db()
        self.assertEqual(question.view_count, 1)

    def test_popular_questions_are_ordered_by_weighted_score(self):
        low_score = self.create_question('low score', view_count=2)
        high_score = self.create_question('high score', view_count=1)
        answer = Answer.objects.create(
            author=self.other_user,
            question=high_score,
            content='answer content',
            create_date=timezone.now(),
        )
        high_score.voter.add(self.other_user)
        Comment.objects.create(
            author=self.other_user,
            question=high_score,
            content='question comment',
            create_date=timezone.now(),
        )
        Comment.objects.create(
            author=self.other_user,
            answer=answer,
            content='answer comment',
            create_date=timezone.now(),
        )

        response = self.client.get(reverse('pybo:popular'))
        questions = list(response.context['question_list'])

        self.assertEqual(questions[0], high_score)
        self.assertEqual(questions[0].popular_score, 11)
        self.assertEqual(questions[0].answer_count, 1)
        self.assertEqual(questions[0].comment_count, 2)
        self.assertEqual(questions[1], low_score)

    def test_popular_questions_with_same_score_are_ordered_by_latest_first(self):
        old_question = self.create_question(
            'old same score',
            view_count=1,
            create_date=timezone.now() - timedelta(days=1),
        )
        new_question = self.create_question('new same score', view_count=1)

        response = self.client.get(reverse('pybo:popular'))
        questions = list(response.context['question_list'])

        self.assertEqual(questions[0], new_question)
        self.assertEqual(questions[1], old_question)

    def test_popular_questions_are_limited_to_top_10(self):
        for index in range(11):
            self.create_question(f'paginated question {index}', view_count=index)

        response = self.client.get(reverse('pybo:popular'), {'page': 2})

        questions = list(response.context['question_list'])
        self.assertEqual(len(questions), 10)
        self.assertEqual(questions[0].subject, 'paginated question 10')
        self.assertEqual(questions[-1].subject, 'paginated question 1')
        self.assertNotIn('paginated question 0', [question.subject for question in questions])
        self.assertNotContains(response, '<ul class="pagination justify-content-center">')
        self.assertNotContains(response, '<th>점수</th>', html=True)
        self.assertNotContains(response, '<th>댓글</th>', html=True)
        self.assertNotContains(response, '이전')
        self.assertNotContains(response, '다음')

    def test_popular_questions_use_pybo_question_list_layout(self):
        question = self.create_question('popular layout question', view_count=1)
        Answer.objects.create(
            author=self.other_user,
            question=question,
            content='answer content',
            create_date=timezone.now(),
        )
        question.voter.add(self.other_user)

        response = self.client.get(reverse('pybo:popular'))

        self.assertContains(response, '<th>번호</th>', html=True)
        self.assertContains(response, '<th>추천</th>', html=True)
        self.assertContains(response, '<th>질문 유형</th>', html=True)
        self.assertContains(response, '<th style="width:50%">제목</th>', html=True)
        self.assertContains(response, '<th>글쓴이</th>', html=True)
        self.assertContains(response, '<th>조회</th>', html=True)
        self.assertContains(response, '<th>작성일시</th>', html=True)
        self.assertContains(
            response,
            '<span class="badge badge-warning px-2 py-1">1</span>',
            html=True,
        )
        self.assertContains(
            response,
            '<span class="text-danger small ml-2">1</span>',
            html=True,
        )


class ReportViewsTests(FastPasswordTestCase):
    def setUp(self):
        self.reporter = User.objects.create_user(username='reporter', password='password')
        self.author = User.objects.create_user(username='author', password='password')
        self.staff = User.objects.create_user(
            username='staff',
            password='password',
            is_staff=True,
        )
        self.category = Category.objects.get(slug='etc')
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
        self.assertEqual(report.target_type, 'question')
        self.assertEqual(report.target_object_id, self.question.id)
        self.assertEqual(report.target_question_id, self.question.id)
        self.assertEqual(report.target_author, self.author.username)
        self.assertEqual(report.target_subject, self.question.subject)
        self.assertEqual(report.target_content, self.question.content)

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

    def test_duplicate_report_is_blocked_by_database_constraint(self):
        ContentReport.objects.create(
            reporter=self.reporter,
            question=self.question,
            reason='spam',
            create_date=timezone.now(),
        )

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                ContentReport.objects.create(
                    reporter=self.reporter,
                    question=self.question,
                    reason='abuse',
                    create_date=timezone.now(),
                )

    def test_report_detail_shows_snapshot_after_target_is_modified(self):
        report = ContentReport.objects.create(
            reporter=self.reporter,
            question=self.question,
            reason='spam',
            create_date=timezone.now(),
        )
        self.question.subject = 'modified report subject'
        self.question.content = 'modified report content'
        self.question.save()
        self.client.login(username='staff', password='password')

        response = self.client.get(reverse('pybo:report_detail', args=[report.id]))

        self.assertContains(response, 'report subject')
        self.assertContains(response, 'report content')
        self.assertNotContains(response, 'modified report content')

    def test_report_detail_survives_deleted_target(self):
        report = ContentReport.objects.create(
            reporter=self.reporter,
            question=self.question,
            reason='spam',
            create_date=timezone.now(),
        )
        self.question.delete()
        report.refresh_from_db()
        self.client.login(username='staff', password='password')

        response = self.client.get(reverse('pybo:report_detail', args=[report.id]))

        self.assertEqual(response.status_code, 200)
        self.assertIsNone(report.question)
        self.assertContains(response, 'report content')
        self.assertContains(response, '원문 삭제됨')
        self.assertNotContains(response, '원문 보기')

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


class NotificationViewsTests(FastPasswordTestCase):
    def setUp(self):
        self.author = User.objects.create_user(username='author', password='password')
        self.actor = User.objects.create_user(username='actor', password='password')
        self.other_user = User.objects.create_user(username='other', password='password')
        self.category = Category.objects.get(slug='etc')
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

        response = self.client.post(reverse('pybo:vote_question', args=[self.question.id]))

        self.assertEqual(response.status_code, 302)
        notification = Notification.objects.get()
        self.assertEqual(notification.recipient, self.author)
        self.assertEqual(notification.notification_type, 'question_vote')
        self.assertEqual(notification.question, self.question)

    def test_question_vote_get_method_is_not_allowed(self):
        self.client.login(username='actor', password='password')

        response = self.client.get(reverse('pybo:vote_question', args=[self.question.id]))

        self.assertEqual(response.status_code, 405)
        self.assertFalse(self.question.voter.filter(id=self.actor.id).exists())

    def test_answer_vote_sends_notification_to_answer_author(self):
        answer = Answer.objects.create(
            question=self.question,
            author=self.author,
            content='answer content',
            create_date=timezone.now(),
        )
        self.client.login(username='actor', password='password')

        response = self.client.post(reverse('pybo:vote_answer', args=[answer.id]))

        self.assertEqual(response.status_code, 302)
        notification = Notification.objects.get()
        self.assertEqual(notification.recipient, self.author)
        self.assertEqual(notification.notification_type, 'answer_vote')
        self.assertEqual(notification.answer, answer)

    def test_answer_vote_get_method_is_not_allowed(self):
        answer = Answer.objects.create(
            question=self.question,
            author=self.author,
            content='answer content',
            create_date=timezone.now(),
        )
        self.client.login(username='actor', password='password')

        response = self.client.get(reverse('pybo:vote_answer', args=[answer.id]))

        self.assertEqual(response.status_code, 405)
        self.assertFalse(answer.voter.filter(id=self.actor.id).exists())

    def test_own_action_does_not_create_notification(self):
        self.client.login(username='author', password='password')

        self.client.post(reverse('pybo:answer_create', args=[self.question.id]), {
            'content': 'own answer',
        })
        self.client.post(reverse('pybo:comment_create_question', args=[self.question.id]), {
            'content': 'own comment',
        })
        self.client.post(reverse('pybo:vote_question', args=[self.question.id]))

        self.assertEqual(Notification.objects.count(), 0)

    def test_repeated_vote_does_not_create_additional_notification(self):
        self.client.login(username='actor', password='password')
        url = reverse('pybo:vote_question', args=[self.question.id])

        self.client.post(url)
        self.client.post(url)

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

        response = self.client.post(reverse('pybo:notification_read', args=[notification.id]))

        self.assertRedirects(response, reverse('pybo:detail', args=[self.question.id]))
        notification.refresh_from_db()
        self.assertIsNotNone(notification.read_date)

    def test_notification_read_get_method_is_not_allowed(self):
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

        self.assertEqual(response.status_code, 405)
        notification.refresh_from_db()
        self.assertIsNone(notification.read_date)


class PyboApiTests(FastPasswordTestCase):
    def setUp(self):
        self.api = APIClient()
        self.user = User.objects.create_user(username='user', password='password')
        self.other_user = User.objects.create_user(username='other', password='password')
        self.staff = User.objects.create_user(username='staff', password='password', is_staff=True)
        self.error_category = Category.objects.get(slug='error')
        self.concept_category = Category.objects.get(slug='concept')
        self.etc_category = Category.objects.get(slug='etc')
        self.error_question = Question.objects.create(
            category=self.error_category,
            author=self.other_user,
            subject='Django error subject',
            content='common keyword',
            create_date=timezone.now(),
            view_count=1,
        )
        self.concept_question = Question.objects.create(
            category=self.concept_category,
            author=self.user,
            subject='concept subject',
            content='other content',
            create_date=timezone.now() - timedelta(days=1),
        )
        self.answer = Answer.objects.create(
            author=self.user,
            question=self.error_question,
            content='answer keyword',
            create_date=timezone.now(),
        )
        self.comment = Comment.objects.create(
            author=self.user,
            question=self.error_question,
            content='comment content',
            create_date=timezone.now(),
        )

    def test_question_api_filters_by_keyword_and_category(self):
        response = self.api.get(reverse('pybo_api:question-list'), {
            'kw': 'answer keyword',
            'category': 'error',
        })

        self.assertEqual(response.status_code, 200)
        subjects = [question['subject'] for question in response.data['results']]
        self.assertIn(self.error_question.subject, subjects)
        self.assertNotIn(self.concept_question.subject, subjects)

    def test_category_api_lists_question_types(self):
        response = self.api.get(reverse('pybo_api:category-list'))

        self.assertEqual(response.status_code, 200)
        slugs = {category['slug'] for category in response.data['results']}
        self.assertEqual(
            slugs,
            {'error', 'concept', 'implementation', 'environment', 'etc'},
        )

    def test_popular_question_api_orders_by_weighted_score(self):
        popular_question = Question.objects.create(
            category=self.etc_category,
            author=self.user,
            subject='popular api subject',
            content='popular api content',
            create_date=timezone.now(),
            view_count=2,
        )
        popular_question.voter.add(self.other_user)
        Answer.objects.create(
            author=self.other_user,
            question=popular_question,
            content='popular answer',
            create_date=timezone.now(),
        )

        response = self.api.get(reverse('pybo_api:popular-question-list'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['results'][0]['subject'], popular_question.subject)
        self.assertEqual(response.data['results'][0]['popular_score'], 10)

    def test_bookmark_api_toggles_and_lists_current_user_bookmarks(self):
        self.api.login(username='user', password='password')

        toggle_response = self.api.post(reverse('pybo_api:bookmark-toggle', args=[self.error_question.id]))
        list_response = self.api.get(reverse('pybo_api:bookmark-list'))
        second_toggle_response = self.api.post(reverse('pybo_api:bookmark-toggle', args=[self.error_question.id]))

        self.assertEqual(toggle_response.status_code, 200)
        self.assertTrue(toggle_response.data['bookmarked'])
        self.assertEqual(list_response.data['results'][0]['id'], self.error_question.id)
        self.assertFalse(second_toggle_response.data['bookmarked'])

    def test_mypage_activity_api_returns_only_current_user_activity(self):
        self.error_question.voter.add(self.user)
        self.error_question.bookmark.add(self.user)
        Comment.objects.create(
            author=self.other_user,
            question=self.concept_question,
            content='other comment',
            create_date=timezone.now(),
        )
        self.api.login(username='user', password='password')

        response = self.api.get(reverse('pybo_api:my-activity'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['my_questions'][0]['id'], self.concept_question.id)
        self.assertEqual(response.data['my_answers'][0]['id'], self.answer.id)
        self.assertEqual(response.data['my_comments'][0]['id'], self.comment.id)
        self.assertEqual(response.data['voted_questions'][0]['id'], self.error_question.id)
        self.assertEqual(response.data['bookmarked_questions'][0]['id'], self.error_question.id)
        self.assertNotIn('other comment', [comment['content'] for comment in response.data['my_comments']])

    def test_report_api_creates_report_and_blocks_invalid_reports(self):
        self.api.login(username='user', password='password')
        url = reverse('pybo_api:report-list-create')

        response = self.api.post(url, {
            'target_type': 'question',
            'target_id': self.error_question.id,
            'reason': 'spam',
            'content': 'spam report',
        }, format='json')
        duplicate_response = self.api.post(url, {
            'target_type': 'question',
            'target_id': self.error_question.id,
            'reason': 'abuse',
            'content': 'duplicate report',
        }, format='json')
        own_response = self.api.post(url, {
            'target_type': 'question',
            'target_id': self.concept_question.id,
            'reason': 'abuse',
            'content': 'own report',
        }, format='json')

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['target_type'], 'question')
        self.assertEqual(response.data['status'], 'pending')
        self.assertEqual(duplicate_response.status_code, 400)
        self.assertEqual(own_response.status_code, 400)
        self.assertEqual(ContentReport.objects.count(), 1)

    def test_report_admin_api_lists_and_reviews_reports(self):
        report = ContentReport.objects.create(
            reporter=self.user,
            question=self.error_question,
            reason='spam',
            create_date=timezone.now(),
        )
        self.api.login(username='user', password='password')

        denied_response = self.api.get(reverse('pybo_api:report-list-create'))

        self.api.logout()
        self.api.login(username='staff', password='password')
        list_response = self.api.get(reverse('pybo_api:report-list-create'))
        review_response = self.api.patch(reverse('pybo_api:report-detail', args=[report.id]), {
            'status': 'resolved',
            'review_memo': '처리했습니다.',
        }, format='json')

        report.refresh_from_db()
        self.assertEqual(denied_response.status_code, 403)
        self.assertEqual(list_response.status_code, 200)
        self.assertEqual(list_response.data['results'][0]['id'], report.id)
        self.assertEqual(review_response.status_code, 200)
        self.assertEqual(report.status, 'resolved')
        self.assertEqual(report.reviewed_by, self.staff)

    def test_notification_api_lists_current_user_notifications_and_marks_read(self):
        notification = Notification.objects.create(
            recipient=self.user,
            actor=self.other_user,
            notification_type='answer',
            question=self.error_question,
            message='user notification',
            create_date=timezone.now(),
        )
        Notification.objects.create(
            recipient=self.other_user,
            actor=self.user,
            notification_type='answer',
            question=self.error_question,
            message='other notification',
            create_date=timezone.now(),
        )
        self.api.login(username='user', password='password')

        list_response = self.api.get(reverse('pybo_api:notification-list'))
        read_response = self.api.patch(reverse('pybo_api:notification-read', args=[notification.id]))

        notification.refresh_from_db()
        self.assertEqual(list_response.status_code, 200)
        self.assertEqual(list_response.data['results'][0]['message'], 'user notification')
        self.assertEqual(read_response.status_code, 200)
        self.assertTrue(read_response.data['is_read'])
        self.assertIsNotNone(notification.read_date)
