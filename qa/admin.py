"""
[과제 3] qa/admin.py
TODO: Question과 Answer 모델을 admin에 등록하세요.
"""
from django.contrib import admin
from .models import Question, Answer

# TODO: Question 모델을 admin에 등록하세요
admin.site.register(Question)

# TODO: Answer 모델을 admin에 등록하세요
admin.site.register(Answer)
