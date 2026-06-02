from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Question(models.Model):
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='author_question')
    subject = models.CharField(max_length=200)
    content = models.TextField()
    create_date = models.DateTimeField()
    modify_date = models.DateTimeField(null=True, blank=True)
    voter = models.ManyToManyField(User, related_name='voter_question')
    bookmark = models.ManyToManyField(User, related_name='bookmark_question', blank=True)

    def __str__(self):
        return self.subject


class Answer(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='author_answer')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    content = models.TextField()
    create_date = models.DateTimeField()
    modify_date = models.DateTimeField(null=True, blank=True)
    voter = models.ManyToManyField(User, related_name='voter_answer')


class Comment(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    create_date = models.DateTimeField()
    modify_date = models.DateTimeField(null=True, blank=True)
    question = models.ForeignKey(Question, null=True, blank=True, on_delete=models.CASCADE)
    answer = models.ForeignKey(Answer, null=True, blank=True, on_delete=models.CASCADE)


class ContentReport(models.Model):
    REASON_CHOICES = [
        ('abuse', '욕설/비방'),
        ('spam', '스팸/홍보'),
        ('inappropriate', '부적절한 내용'),
        ('privacy', '개인정보 노출'),
        ('other', '기타'),
    ]
    STATUS_CHOICES = [
        ('pending', '접수'),
        ('reviewing', '검토중'),
        ('resolved', '처리완료'),
        ('rejected', '기각'),
    ]

    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='content_reports')
    question = models.ForeignKey(Question, null=True, blank=True, on_delete=models.CASCADE, related_name='reports')
    answer = models.ForeignKey(Answer, null=True, blank=True, on_delete=models.CASCADE, related_name='reports')
    comment = models.ForeignKey(Comment, null=True, blank=True, on_delete=models.CASCADE, related_name='reports')
    reason = models.CharField(max_length=20, choices=REASON_CHOICES)
    content = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    create_date = models.DateTimeField()
    reviewed_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='reviewed_content_reports',
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    review_memo = models.TextField(blank=True)

    class Meta:
        ordering = ['-create_date']

    def clean(self):
        targets = [self.question_id, self.answer_id, self.comment_id]
        if sum(1 for target in targets if target) != 1:
            raise ValidationError('신고 대상은 질문, 답변, 댓글 중 하나여야 합니다.')

    def __str__(self):
        return f'{self.get_target_type_display()} 신고 #{self.id}'

    @property
    def target(self):
        return self.question or self.answer or self.comment

    @property
    def target_question_id(self):
        if self.question_id:
            return self.question_id
        if self.answer_id:
            return self.answer.question_id
        if self.comment_id and self.comment.question_id:
            return self.comment.question_id
        if self.comment_id and self.comment.answer_id:
            return self.comment.answer.question_id
        return None

    def get_target_type_display(self):
        if self.question_id:
            return '질문'
        if self.answer_id:
            return '답변'
        return '댓글'


class Notification(models.Model):
    TYPE_CHOICES = [
        ('answer', '답변'),
        ('comment', '댓글'),
        ('question_vote', '질문 추천'),
        ('answer_vote', '답변 추천'),
    ]

    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    actor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_notifications')
    notification_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    question = models.ForeignKey(Question, null=True, blank=True, on_delete=models.CASCADE)
    answer = models.ForeignKey(Answer, null=True, blank=True, on_delete=models.CASCADE)
    comment = models.ForeignKey(Comment, null=True, blank=True, on_delete=models.CASCADE)
    message = models.CharField(max_length=255)
    create_date = models.DateTimeField()
    read_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-create_date']

    def __str__(self):
        return self.message

    @property
    def target_question_id(self):
        if self.question_id:
            return self.question_id
        if self.answer_id:
            return self.answer.question_id
        if self.comment_id and self.comment.question_id:
            return self.comment.question_id
        if self.comment_id and self.comment.answer_id:
            return self.comment.answer.question_id
        return None
