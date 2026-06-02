from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from ..models import Question


@login_required(login_url='common:login')
def bookmark_question(request, question_id):
    """
    pybo 질문 북마크 등록/해제
    """
    question = get_object_or_404(Question, pk=question_id)
    if question.bookmark.filter(id=request.user.id).exists():
        question.bookmark.remove(request.user)
    else:
        question.bookmark.add(request.user)
    return redirect('pybo:detail', question_id=question.id)


@login_required(login_url='common:login')
def bookmark_list(request):
    """
    pybo 내 북마크 목록 출력
    """
    page = request.GET.get('page', '1')
    question_list = request.user.bookmark_question.order_by('-create_date')

    paginator = Paginator(question_list, 10)
    page_obj = paginator.get_page(page)

    context = {'question_list': page_obj}
    return render(request, 'pybo/bookmark_list.html', context)
