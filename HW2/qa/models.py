"""
[과제 3] qa/models.py
TODO: Question과 Answer 모델을 완성하세요.

Question 모델 필드:
  - title: CharField(max_length=200)
  - content: TextField()
  - author: ForeignKey(User, on_delete=models.CASCADE)
  - created_at: DateTimeField(auto_now_add=True)

Answer 모델 필드:
  - question: ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
  - content: TextField()
  - author: ForeignKey(User, on_delete=models.CASCADE)
  - created_at: DateTimeField(auto_now_add=True)
"""
from django.db import models
from django.contrib.auth.models import User


class Question(models.Model):
    # TODO: 제목 필드 (CharField, max_length=200)
    title = models.CharField(max_length=200)

    # TODO: 내용 필드 (TextField)
    content = models.TextField()

    # TODO: 작성자 필드 (ForeignKey → User, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    # TODO: 작성일 필드 (DateTimeField, auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Answer(models.Model):
    # TODO: 질문 참조 필드 (ForeignKey → Question, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')

    # TODO: 답변 내용 필드 (TextField)
    content = models.TextField()

    # TODO: 작성자 필드 (ForeignKey → User, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    # TODO: 작성일 필드 (DateTimeField, auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Answer to {self.question.title} by {self.author.username}"
