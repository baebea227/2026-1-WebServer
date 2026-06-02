from django.contrib import admin

from .models import Answer, Category, Comment, ContentReport, Notification, Question


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('subject', 'category', 'author', 'create_date')
    search_fields = ('subject', 'content', 'author__username')
    list_filter = ('category',)


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('question', 'author', 'create_date')
    search_fields = ('content', 'author__username', 'question__subject')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'create_date', 'question', 'answer')
    search_fields = ('content', 'author__username')


@admin.register(ContentReport)
class ContentReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_target_type_display', 'reason', 'status', 'reporter', 'create_date', 'reviewed_by')
    list_filter = ('status', 'reason', 'create_date')
    search_fields = ('content', 'review_memo', 'reporter__username')
    readonly_fields = ('reporter', 'question', 'answer', 'comment', 'reason', 'content', 'create_date')


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'notification_type', 'recipient', 'actor', 'create_date', 'read_date')
    list_filter = ('notification_type', 'create_date', 'read_date')
    search_fields = ('message', 'recipient__username', 'actor__username')
