from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect

from ..models import Question, Answer
from ..notifications import create_notification


@login_required(login_url='common:login')
def vote_question(request, question_id):
    """
    pybo 질문추천등록
    """
    question = get_object_or_404(Question, pk=question_id)
    if request.user == question.author:
        messages.error(request, '본인이 작성한 글은 추천할수 없습니다')
    elif question.voter.filter(id=request.user.id).exists():
        messages.error(request, '이미 추천한 글입니다')
    else:
        question.voter.add(request.user)
        create_notification(
            recipient=question.author,
            actor=request.user,
            notification_type='question_vote',
            question=question,
            message=f'{request.user.username}님이 질문을 추천했습니다.',
        )
    return redirect('pybo:detail', question_id=question.id)


@login_required(login_url='common:login')
def vote_answer(request, answer_id):
    """
    pybo 답글추천등록
    """
    answer = get_object_or_404(Answer, pk=answer_id)
    if request.user == answer.author:
        messages.error(request, '본인이 작성한 글은 추천할수 없습니다')
    elif answer.voter.filter(id=request.user.id).exists():
        messages.error(request, '이미 추천한 글입니다')
    else:
        answer.voter.add(request.user)
        create_notification(
            recipient=answer.author,
            actor=request.user,
            notification_type='answer_vote',
            answer=answer,
            message=f'{request.user.username}님이 답변을 추천했습니다.',
        )
    return redirect('pybo:detail', question_id=answer.question.id)
