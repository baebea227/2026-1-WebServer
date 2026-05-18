from django.urls import path

from . import api_views

app_name = 'pybo_api'

urlpatterns = [
    path('request-info/', api_views.request_info, name='request_info'),
    path('auth/login/', api_views.auth_login, name='auth_login'),
    path('auth/logout/', api_views.auth_logout, name='auth_logout'),
    path('auth/me/', api_views.auth_me, name='auth_me'),
    path('questions/', api_views.question_list, name='question_list'),
    path('questions/<int:question_id>/bookmark/', api_views.question_bookmark, name='question_bookmark'),
    path('bookmarks/', api_views.bookmark_list, name='bookmark_list'),
    path('board/summary/', api_views.board_summary, name='board_summary'),
]
