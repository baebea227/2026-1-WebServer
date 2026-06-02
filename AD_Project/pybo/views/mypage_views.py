from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from ..models import Answer, Comment, Question


@login_required(login_url='common:login')
def mypage(request):
    """
    로그인 사용자의 최근 활동을 한 화면에 출력
    """
    user = request.user
    limit = 10

    context = {
        'my_questions': Question.objects.select_related('category', 'author')
        .filter(author=user)
        .order_by('-create_date')[:limit],
        'my_answers': Answer.objects.select_related('question', 'author')
        .filter(author=user)
        .order_by('-create_date')[:limit],
        'my_comments': Comment.objects.select_related('question', 'answer__question', 'author')
        .filter(author=user)
        .order_by('-create_date')[:limit],
        'voted_questions': user.voter_question.select_related('category', 'author')
        .order_by('-create_date')[:limit],
        'voted_answers': user.voter_answer.select_related('question', 'author')
        .order_by('-create_date')[:limit],
        'bookmarked_questions': user.bookmark_question.select_related('category', 'author')
        .order_by('-create_date')[:limit],
    }
    return render(request, 'pybo/mypage.html', context)
