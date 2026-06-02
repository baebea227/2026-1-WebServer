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
    view_count = models.PositiveIntegerField(default=0)
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
    TARGET_TYPE_CHOICES = [
        ('question', '질문'),
        ('answer', '답변'),
        ('comment', '댓글'),
    ]
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
    question = models.ForeignKey(Question, null=True, blank=True, on_delete=models.SET_NULL, related_name='reports')
    answer = models.ForeignKey(Answer, null=True, blank=True, on_delete=models.SET_NULL, related_name='reports')
    comment = models.ForeignKey(Comment, null=True, blank=True, on_delete=models.SET_NULL, related_name='reports')
    target_type = models.CharField(max_length=20, choices=TARGET_TYPE_CHOICES)
    target_object_id = models.PositiveIntegerField()
    target_question_id = models.PositiveIntegerField()
    target_author = models.CharField(max_length=150, blank=True)
    target_subject = models.CharField(max_length=200, blank=True)
    target_content = models.TextField(blank=True)
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
        constraints = [
            models.UniqueConstraint(
                fields=['reporter', 'target_type', 'target_object_id'],
                name='unique_content_report_target',
            ),
        ]

    def clean(self):
        targets = [self.question_id, self.answer_id, self.comment_id]
        target_count = sum(1 for target in targets if target)
        has_snapshot = self.target_type and self.target_object_id and self.target_question_id
        if target_count > 1 or (target_count == 0 and not has_snapshot):
            raise ValidationError('신고 대상은 질문, 답변, 댓글 중 하나여야 합니다.')

    def __str__(self):
        return f'{self.get_target_type_display()} 신고 #{self.id}'

    def save(self, *args, **kwargs):
        self.populate_snapshot()
        super().save(*args, **kwargs)

    @property
    def target(self):
        return self.question or self.answer or self.comment

    @property
    def current_question_id(self):
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
        target_type = self.target_type or self._infer_target_type()
        return dict(self.TARGET_TYPE_CHOICES).get(target_type, '신고 대상')

    def populate_snapshot(self, force=False):
        snapshot = self._build_snapshot()
        if not snapshot:
            return

        for field, value in snapshot.items():
            if force or not getattr(self, field):
                setattr(self, field, value)

    def _infer_target_type(self):
        if self.question_id:
            return 'question'
        if self.answer_id:
            return 'answer'
        if self.comment_id:
            return 'comment'
        return ''

    def _build_snapshot(self):
        if self.question_id:
            question = self.question
            return {
                'target_type': 'question',
                'target_object_id': question.id,
                'target_question_id': question.id,
                'target_author': question.author.username,
                'target_subject': question.subject,
                'target_content': question.content,
            }
        if self.answer_id:
            answer = self.answer
            return {
                'target_type': 'answer',
                'target_object_id': answer.id,
                'target_question_id': answer.question_id,
                'target_author': answer.author.username,
                'target_subject': answer.question.subject,
                'target_content': answer.content,
            }
        if self.comment_id:
            comment = self.comment
            question = comment.question or comment.answer.question
            return {
                'target_type': 'comment',
                'target_object_id': comment.id,
                'target_question_id': question.id,
                'target_author': comment.author.username,
                'target_subject': question.subject,
                'target_content': comment.content,
            }
        return None


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
