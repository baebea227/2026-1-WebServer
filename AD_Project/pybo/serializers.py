from rest_framework import serializers

from .models import Answer, Category, Comment, ContentReport, Notification, Question


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description']


class QuestionSummarySerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    author = serializers.CharField(source='author.username', read_only=True)
    vote_count = serializers.IntegerField(read_only=True, default=0)
    answer_count = serializers.IntegerField(read_only=True, default=0)
    comment_count = serializers.IntegerField(read_only=True, default=0)
    popular_score = serializers.IntegerField(read_only=True, default=0)
    bookmarked = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = [
            'id',
            'category',
            'author',
            'subject',
            'content',
            'create_date',
            'modify_date',
            'view_count',
            'vote_count',
            'answer_count',
            'comment_count',
            'popular_score',
            'bookmarked',
        ]

    def get_bookmarked(self, question):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return question.bookmark.filter(id=request.user.id).exists()


class AnswerSummarySerializer(serializers.ModelSerializer):
    author = serializers.CharField(source='author.username', read_only=True)
    question_id = serializers.IntegerField(source='question.id', read_only=True)
    question_subject = serializers.CharField(source='question.subject', read_only=True)
    vote_count = serializers.SerializerMethodField()

    class Meta:
        model = Answer
        fields = ['id', 'question_id', 'question_subject', 'author', 'content', 'create_date', 'modify_date', 'vote_count']

    def get_vote_count(self, answer):
        return answer.voter.count()


class CommentSummarySerializer(serializers.ModelSerializer):
    author = serializers.CharField(source='author.username', read_only=True)
    question_id = serializers.SerializerMethodField()
    question_subject = serializers.SerializerMethodField()
    answer_id = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'question_id', 'question_subject', 'answer_id', 'author', 'content', 'create_date', 'modify_date']

    def get_question_id(self, comment):
        if comment.question_id:
            return comment.question_id
        if comment.answer_id:
            return comment.answer.question_id
        return None

    def get_question_subject(self, comment):
        if comment.question_id:
            return comment.question.subject
        if comment.answer_id:
            return comment.answer.question.subject
        return ''

    def get_answer_id(self, comment):
        return comment.answer_id


class ContentReportSerializer(serializers.ModelSerializer):
    reporter = serializers.CharField(source='reporter.username', read_only=True)
    reviewed_by = serializers.SerializerMethodField()
    target_type_display = serializers.CharField(source='get_target_type_display', read_only=True)

    class Meta:
        model = ContentReport
        fields = [
            'id',
            'reporter',
            'target_type',
            'target_type_display',
            'target_object_id',
            'target_question_id',
            'target_author',
            'target_subject',
            'target_content',
            'reason',
            'content',
            'status',
            'create_date',
            'reviewed_by',
            'reviewed_at',
            'review_memo',
        ]

    def get_reviewed_by(self, report):
        if report.reviewed_by_id:
            return report.reviewed_by.username
        return None


class ReportCreateSerializer(serializers.Serializer):
    target_type = serializers.ChoiceField(choices=ContentReport.TARGET_TYPE_CHOICES)
    target_id = serializers.IntegerField(min_value=1)
    reason = serializers.ChoiceField(choices=ContentReport.REASON_CHOICES)
    content = serializers.CharField(required=False, allow_blank=True)


class ReportReviewSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=ContentReport.STATUS_CHOICES, required=False)
    review_memo = serializers.CharField(required=False, allow_blank=True)


class NotificationSerializer(serializers.ModelSerializer):
    actor = serializers.CharField(source='actor.username', read_only=True)
    target_question_id = serializers.IntegerField(read_only=True)
    is_read = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = [
            'id',
            'notification_type',
            'actor',
            'message',
            'target_question_id',
            'create_date',
            'read_date',
            'is_read',
        ]

    def get_is_read(self, notification):
        return notification.read_date is not None
