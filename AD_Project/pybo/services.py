from dataclasses import dataclass
from typing import Any

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.db.models import Count, Q, QuerySet
from django.utils import timezone

from .exceptions import AuthenticationRequiredError, InvalidCredentialsError, NotFoundError, ValidationError
from .models import Answer, Bookmark, Comment, Question


def _django_request(request: Any) -> Any:
    return getattr(request, '_request', request)


def _single_or_list(query_params: Any, key: str) -> str | list[str]:
    values = query_params.getlist(key)
    if len(values) == 1:
        return values[0]
    return values


def require_authenticated_user(user: Any) -> User:
    if not getattr(user, 'is_authenticated', False):
        raise AuthenticationRequiredError()
    return user


@dataclass(frozen=True)
class RequestMessage:
    method: str
    path: str
    query_params: dict[str, str | list[str]]
    user_agent: str
    client_ip: str
    message: str

    @classmethod
    def from_request(cls, request: Any) -> 'RequestMessage':
        django_request = _django_request(request)
        query_params = {
            key: _single_or_list(django_request.GET, key)
            for key in django_request.GET.keys()
        }
        forwarded_for = django_request.META.get('HTTP_X_FORWARDED_FOR', '')
        client_ip = forwarded_for.split(',')[0].strip() if forwarded_for else django_request.META.get('REMOTE_ADDR', '')
        return cls(
            method=django_request.method,
            path=django_request.path,
            query_params=query_params,
            user_agent=django_request.META.get('HTTP_USER_AGENT', ''),
            client_ip=client_ip,
            message='Request 객체에서 HTTP 요청 메시지를 읽었습니다.',
        )

    def as_dict(self) -> dict[str, Any]:
        return {
            'method': self.method,
            'path': self.path,
            'query_params': self.query_params,
            'user_agent': self.user_agent,
            'client_ip': self.client_ip,
            'message': self.message,
        }


@dataclass(frozen=True)
class BookmarkToggleResult:
    question_id: int
    bookmarked: bool
    bookmark_count: int

    @classmethod
    def from_question(cls, question: Question, bookmarked: bool) -> 'BookmarkToggleResult':
        return cls(
            question_id=question.id,
            bookmarked=bookmarked,
            bookmark_count=question.bookmarks.count(),
        )

    def as_dict(self) -> dict[str, Any]:
        return {
            'question_id': self.question_id,
            'bookmarked': self.bookmarked,
            'bookmark_count': self.bookmark_count,
        }


@dataclass(frozen=True)
class PopularQuestion:
    id: int
    subject: str
    author: str
    vote_count: int
    answer_count: int
    bookmark_count: int

    @classmethod
    def from_question(cls, question: Question) -> 'PopularQuestion':
        return cls(
            id=question.id,
            subject=question.subject,
            author=question.author.username,
            vote_count=getattr(question, 'vote_count', question.voter.count()),
            answer_count=getattr(question, 'answer_count', question.answer_set.count()),
            bookmark_count=getattr(question, 'bookmark_count', question.bookmarks.count()),
        )

    def as_dict(self) -> dict[str, Any]:
        return {
            'id': self.id,
            'subject': self.subject,
            'author': self.author,
            'vote_count': self.vote_count,
            'answer_count': self.answer_count,
            'bookmark_count': self.bookmark_count,
        }


@dataclass(frozen=True)
class BoardSummary:
    question_count: int
    answer_count: int
    comment_count: int
    vote_count: int
    bookmark_count: int
    popular_questions: list[PopularQuestion]

    @classmethod
    def from_database(cls) -> 'BoardSummary':
        popular_questions = (
            Question.objects.select_related('author')
            .annotate(
                vote_count=Count('voter', distinct=True),
                answer_count=Count('answer', distinct=True),
                bookmark_count=Count('bookmarks', distinct=True),
            )
            .order_by('-vote_count', '-bookmark_count', '-create_date')[:5]
        )
        return cls(
            question_count=Question.objects.count(),
            answer_count=Answer.objects.count(),
            comment_count=Comment.objects.count(),
            vote_count=sum(question.voter.count() for question in Question.objects.all()),
            bookmark_count=Bookmark.objects.count(),
            popular_questions=[PopularQuestion.from_question(question) for question in popular_questions],
        )

    def as_dict(self) -> dict[str, Any]:
        return {
            'question_count': self.question_count,
            'answer_count': self.answer_count,
            'comment_count': self.comment_count,
            'vote_count': self.vote_count,
            'bookmark_count': self.bookmark_count,
            'popular_questions': [question.as_dict() for question in self.popular_questions],
        }


def login_user(request: Any, username: str | None, password: str | None) -> User:
    if not username or not password:
        raise ValidationError('username과 password를 모두 입력해야 합니다.')
    django_request = _django_request(request)
    user = authenticate(django_request, username=username, password=password)
    if user is None:
        raise InvalidCredentialsError()
    login(django_request, user)
    return user


def logout_user(request: Any) -> None:
    logout(_django_request(request))


def search_questions(keyword: str = '', order: str = 'recent') -> QuerySet[Question]:
    questions = Question.objects.select_related('author').annotate(
        vote_count=Count('voter', distinct=True),
        answer_count=Count('answer', distinct=True),
        bookmark_count=Count('bookmarks', distinct=True),
    )
    if keyword:
        questions = questions.filter(
            Q(subject__icontains=keyword)
            | Q(content__icontains=keyword)
            | Q(author__username__icontains=keyword)
            | Q(answer__content__icontains=keyword)
        ).distinct()

    if order == 'votes':
        return questions.order_by('-vote_count', '-create_date')
    if order == 'answers':
        return questions.order_by('-answer_count', '-create_date')
    if order == 'bookmarks':
        return questions.order_by('-bookmark_count', '-create_date')
    return questions.order_by('-create_date')


def toggle_question_bookmark(user: Any, question_id: int) -> BookmarkToggleResult:
    user = require_authenticated_user(user)
    try:
        question = Question.objects.get(pk=question_id)
    except Question.DoesNotExist as exc:
        raise NotFoundError('질문을 찾을 수 없습니다.') from exc

    bookmark, created = Bookmark.objects.get_or_create(
        user=user,
        question=question,
        defaults={'create_date': timezone.now()},
    )
    if not created:
        bookmark.delete()
    return BookmarkToggleResult.from_question(question, created)


def list_user_bookmarks(user: Any) -> QuerySet[Bookmark]:
    user = require_authenticated_user(user)
    return Bookmark.objects.filter(user=user).select_related('question', 'question__author')
