from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import ContentReport
from .serializers import (
    AnswerSummarySerializer,
    CategorySerializer,
    CommentSummarySerializer,
    ContentReportSerializer,
    NotificationSerializer,
    QuestionSummarySerializer,
    ReportCreateSerializer,
    ReportReviewSerializer,
)
from .services import ActivityService, BookmarkService, CategoryService, NotificationService, QuestionQueryService, ReportService


def list_response(serializer):
    return Response({
        'count': len(serializer.data),
        'results': serializer.data,
    })


class QuestionListAPIView(APIView):
    def get(self, request):
        questions = QuestionQueryService.list_questions(
            keyword=request.query_params.get('kw', ''),
            category_slug=request.query_params.get('category', ''),
        )
        serializer = QuestionSummarySerializer(questions, many=True, context={'request': request})
        return list_response(serializer)


class PopularQuestionListAPIView(APIView):
    def get(self, request):
        questions = QuestionQueryService.popular_questions()
        serializer = QuestionSummarySerializer(questions, many=True, context={'request': request})
        return list_response(serializer)


class CategoryListAPIView(APIView):
    def get(self, request):
        serializer = CategorySerializer(CategoryService.list_categories(), many=True)
        return list_response(serializer)


class BookmarkToggleAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, question_id):
        result = BookmarkService.toggle_question(request.user, question_id)
        return Response({
            'question_id': result['question'].id,
            'bookmarked': result['bookmarked'],
            'bookmark_count': result['bookmark_count'],
        })


class BookmarkListAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        questions = BookmarkService.list_user_bookmarks(request.user)
        serializer = QuestionSummarySerializer(questions, many=True, context={'request': request})
        return list_response(serializer)


class MyActivityAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        activity = ActivityService.user_activity(request.user)
        return Response({
            'my_questions': QuestionSummarySerializer(
                activity['my_questions'],
                many=True,
                context={'request': request},
            ).data,
            'my_answers': AnswerSummarySerializer(activity['my_answers'], many=True).data,
            'my_comments': CommentSummarySerializer(activity['my_comments'], many=True).data,
            'voted_questions': QuestionSummarySerializer(
                activity['voted_questions'],
                many=True,
                context={'request': request},
            ).data,
            'voted_answers': AnswerSummarySerializer(activity['voted_answers'], many=True).data,
            'bookmarked_questions': QuestionSummarySerializer(
                activity['bookmarked_questions'],
                many=True,
                context={'request': request},
            ).data,
        })


class ReportListCreateAPIView(APIView):
    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.IsAdminUser()]
        return [permissions.IsAuthenticated()]

    def get(self, request):
        reports = ReportService.list_reports(request.query_params.get('status', ''))
        serializer = ContentReportSerializer(reports, many=True)
        return list_response(serializer)

    def post(self, request):
        serializer = ReportCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            report = ReportService.create_report(reporter=request.user, **serializer.validated_data)
        except ValidationError as exc:
            return Response({'detail': exc.messages[0]}, status=status.HTTP_400_BAD_REQUEST)

        return Response(ContentReportSerializer(report).data, status=status.HTTP_201_CREATED)


class ReportDetailAPIView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def patch(self, request, report_id):
        report = get_object_or_404(ContentReport, pk=report_id)
        serializer = ReportReviewSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        report = ReportService.review_report(report, request.user, serializer.validated_data)
        return Response(ContentReportSerializer(report).data)


class NotificationListAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        notifications = NotificationService.list_user_notifications(request.user)
        serializer = NotificationSerializer(notifications, many=True)
        return list_response(serializer)


class NotificationReadAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, notification_id):
        notification = NotificationService.mark_as_read(request.user, notification_id)
        return Response(NotificationSerializer(notification).data)
