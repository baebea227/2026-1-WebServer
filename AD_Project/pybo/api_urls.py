from django.urls import path

from . import api_views

app_name = 'pybo_api'

urlpatterns = [
    path('questions/', api_views.QuestionListAPIView.as_view(), name='question-list'),
    path('questions/popular/', api_views.PopularQuestionListAPIView.as_view(), name='popular-question-list'),
    path('questions/<int:question_id>/bookmark/', api_views.BookmarkToggleAPIView.as_view(), name='bookmark-toggle'),
    path('categories/', api_views.CategoryListAPIView.as_view(), name='category-list'),
    path('bookmarks/', api_views.BookmarkListAPIView.as_view(), name='bookmark-list'),
    path('me/activities/', api_views.MyActivityAPIView.as_view(), name='my-activity'),
    path('reports/', api_views.ReportListCreateAPIView.as_view(), name='report-list-create'),
    path('reports/<int:report_id>/', api_views.ReportDetailAPIView.as_view(), name='report-detail'),
    path('notifications/', api_views.NotificationListAPIView.as_view(), name='notification-list'),
    path('notifications/<int:notification_id>/read/', api_views.NotificationReadAPIView.as_view(), name='notification-read'),
]
