from __future__ import annotations

from typing import Any

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.db.models import Count, ExpressionWrapper, F, IntegerField, Q, QuerySet
from django.shortcuts import get_object_or_404
from django.utils import timezone

from .models import Answer, Category, Comment, ContentReport, Notification, Question


class QuestionQueryService:
    @classmethod
    def with_metrics(cls, queryset: QuerySet[Question]) -> QuerySet[Question]:
        return queryset.annotate(
            vote_count=Count('voter', distinct=True),
            answer_count=Count('answer', distinct=True),
            question_comment_count=Count('comment', distinct=True),
            answer_comment_count=Count('answer__comment', distinct=True),
        ).annotate(
            comment_count=F('question_comment_count') + F('answer_comment_count'),
            popular_score=ExpressionWrapper(
                F('vote_count') * 5 + F('answer_count') * 3 + F('comment_count') + F('view_count'),
                output_field=IntegerField(),
            ),
        )

    @classmethod
    def list_questions(cls, keyword: str = '', category_slug: str = '') -> QuerySet[Question]:
        queryset = Question.objects.select_related('category', 'author')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        if keyword:
            queryset = queryset.filter(
                Q(subject__icontains=keyword) |
                Q(content__icontains=keyword) |
                Q(answer__content__icontains=keyword) |
                Q(author__username__icontains=keyword) |
                Q(answer__author__username__icontains=keyword)
            ).distinct()
        return cls.with_metrics(queryset).order_by('-create_date')

    @classmethod
    def popular_questions(cls, limit: int = 10) -> QuerySet[Question]:
        queryset = Question.objects.select_related('category', 'author')
        return cls.with_metrics(queryset).order_by('-popular_score', '-create_date')[:limit]


class BookmarkService:
    @classmethod
    def toggle_question(cls, user: User, question_id: int) -> dict[str, Any]:
        question = get_object_or_404(Question, pk=question_id)
        if question.bookmark.filter(id=user.id).exists():
            question.bookmark.remove(user)
            bookmarked = False
        else:
            question.bookmark.add(user)
            bookmarked = True

        return {
            'question': question,
            'bookmarked': bookmarked,
            'bookmark_count': question.bookmark.count(),
        }

    @classmethod
    def list_user_bookmarks(cls, user: User) -> QuerySet[Question]:
        queryset = user.bookmark_question.select_related('category', 'author')
        return QuestionQueryService.with_metrics(queryset).order_by('-create_date')


class ActivityService:
    @classmethod
    def user_activity(cls, user: User, limit: int = 10) -> dict[str, QuerySet]:
        return {
            'my_questions': QuestionQueryService.with_metrics(
                Question.objects.select_related('category', 'author').filter(author=user)
            )
            .order_by('-create_date')[:limit],
            'my_answers': Answer.objects.select_related('question', 'author')
            .filter(author=user)
            .order_by('-create_date')[:limit],
            'my_comments': Comment.objects.select_related('question', 'answer__question', 'author')
            .filter(author=user)
            .order_by('-create_date')[:limit],
            'voted_questions': QuestionQueryService.with_metrics(
                user.voter_question.select_related('category', 'author')
            )
            .order_by('-create_date')[:limit],
            'voted_answers': user.voter_answer.select_related('question', 'author')
            .order_by('-create_date')[:limit],
            'bookmarked_questions': QuestionQueryService.with_metrics(
                user.bookmark_question.select_related('category', 'author')
            )
            .order_by('-create_date')[:limit],
        }


class ReportService:
    @classmethod
    def create_report(
        cls,
        reporter: User,
        target_type: str,
        target_id: int,
        reason: str,
        content: str = '',
    ) -> ContentReport:
        target, target_fields = cls._get_report_target(target_type, target_id)

        if target.author == reporter:
            raise ValidationError('본인이 작성한 콘텐츠는 신고할 수 없습니다.')

        if ContentReport.objects.filter(
            reporter=reporter,
            target_type=target_type,
            target_object_id=target.id,
        ).exists():
            raise ValidationError('이미 신고한 콘텐츠입니다.')

        report = ContentReport(
            reporter=reporter,
            reason=reason,
            content=content,
            create_date=timezone.now(),
            **target_fields,
        )
        try:
            report.save()
        except IntegrityError as exc:
            raise ValidationError('이미 신고한 콘텐츠입니다.') from exc
        return report

    @classmethod
    def list_reports(cls, status_filter: str = '') -> QuerySet[ContentReport]:
        queryset = ContentReport.objects.select_related(
            'reporter',
            'reviewed_by',
            'question',
            'answer',
            'answer__question',
            'comment',
            'comment__question',
            'comment__answer',
            'comment__answer__question',
        )
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        return queryset

    @classmethod
    def review_report(cls, report: ContentReport, reviewer: User, data: dict[str, Any]) -> ContentReport:
        if 'status' in data:
            report.status = data['status']
        if 'review_memo' in data:
            report.review_memo = data['review_memo']
        report.reviewed_by = reviewer
        report.reviewed_at = timezone.now()
        report.save()
        return report

    @classmethod
    def _get_report_target(cls, target_type: str, target_id: int) -> tuple[Question | Answer | Comment, dict[str, Any]]:
        if target_type == 'question':
            target = get_object_or_404(Question, pk=target_id)
            return target, {'question': target}
        if target_type == 'answer':
            target = get_object_or_404(Answer.objects.select_related('question'), pk=target_id)
            return target, {'answer': target}
        if target_type == 'comment':
            target = get_object_or_404(
                Comment.objects.select_related('question', 'answer__question'),
                pk=target_id,
            )
            return target, {'comment': target}
        raise ValidationError('지원하지 않는 신고 대상입니다.')


class NotificationService:
    @classmethod
    def list_user_notifications(cls, user: User) -> QuerySet[Notification]:
        return user.notifications.select_related(
            'actor',
            'question',
            'answer__question',
            'comment__question',
            'comment__answer__question',
        )

    @classmethod
    def mark_as_read(cls, user: User, notification_id: int) -> Notification:
        notification = get_object_or_404(Notification, pk=notification_id, recipient=user)
        if notification.read_date is None:
            notification.read_date = timezone.now()
            notification.save(update_fields=['read_date'])
        return notification


class CategoryService:
    @classmethod
    def list_categories(cls) -> QuerySet[Category]:
        return Category.objects.order_by('id')
