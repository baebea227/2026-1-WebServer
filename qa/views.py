"""
[과제 3] qa/views.py
TODO: 질문 목록, 질문 상세, 질문 작성 뷰를 완성하세요.
"""
from django.shortcuts import render, get_object_or_404, redirect
from .models import Question, Answer
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib.auth.models import User


def question_list(request):
    """질문 목록 뷰: 최신순으로 정렬된 모든 질문을 표시"""
    # TODO: Question을 created_at 역순으로 정렬하여 가져오세요
    # 힌트: Question.objects.order_by('-created_at')
    questions = Question.objects.order_by('-created_at')

    return render(request, 'qa/question_list.html', {'questions': questions})


def question_detail(request, pk):
    """질문 상세 뷰: 질문 내용과 답변 목록을 표시하고, 답변 작성 처리"""
    # TODO: pk로 Question을 가져오세요 (없으면 404)
    # 힌트: get_object_or_404(Question, pk=pk)
    question = get_object_or_404(Question, pk=pk)

    if request.method == 'POST':
        content = request.POST.get('content')
        if content and request.user.is_authenticated:
            # TODO: Answer 객체를 생성하세요
            # 힌트: Answer.objects.create(question=..., content=..., author=..., created_at=...)
            Answer.objects.create(
                question=question,
                content=content,
                author=request.user,
                created_at=timezone.now()
            )
            return redirect('question_detail', pk=pk)

    return render(request, 'qa/question_detail.html', {'question': question})


# TODO: 이 뷰에 @login_required 데코레이터를 적용하세요
@login_required
def ask_question(request):
    """질문 작성 뷰: 로그인한 사용자만 질문을 작성할 수 있음"""
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        if title and content:
            # TODO: Question 객체를 생성하세요
            Question.objects.create(
                title=title,
                content=content,
                author=request.user,
                created_at=timezone.now()
            )
            # TODO: 질문 목록 페이지로 redirect하세요
            # 힌트: redirect('question_list')
            return redirect('question_list')

    return render(request, 'qa/ask_question.html')
