from django.core.paginator import Paginator
from django.db.models import Count, ExpressionWrapper, F, IntegerField, Q
from django.shortcuts import render, get_object_or_404

from ..models import Category, Question


def index(request):
    """
    pybo 목록 출력
    """
    # 입력 파라미터
    page = request.GET.get('page', '1')  # 페이지
    kw = request.GET.get('kw', '')  # 검색어
    category_slug = request.GET.get('category', '')  # 질문 유형

    # 조회
    category_list = Category.objects.order_by('id')
    question_list = Question.objects.select_related('category', 'author').order_by('-create_date')
    if category_slug:
        question_list = question_list.filter(category__slug=category_slug)
    if kw:
        question_list = question_list.filter(
            Q(subject__icontains=kw) |  # 제목 검색
            Q(content__icontains=kw) |  # 내용 검색
            Q(answer__content__icontains=kw) |  # 답변 내용 검색
            Q(author__username__icontains=kw) |  # 질문 글쓴이 검색
            Q(answer__author__username__icontains=kw)  # 답변 글쓴이 검색
        ).distinct()

    # 페이징처리
    paginator = Paginator(question_list, 10)  # 페이지당 10개씩 보여주기
    page_obj = paginator.get_page(page)

    context = {
        'question_list': page_obj,
        'page': page,
        'kw': kw,
        'category': category_slug,
        'category_list': category_list,
    }
    return render(request, 'pybo/question_list.html', context)


def popular(request):
    """
    인기 질문 목록 출력
    """
    question_list = Question.objects.select_related('category', 'author').annotate(
        vote_count=Count('voter', distinct=True),
        answer_count=Count('answer', distinct=True),
        question_comment_count=Count('comment', distinct=True),
        answer_comment_count=Count('answer__comment', distinct=True),
    ).annotate(
        comment_count=F('question_comment_count') + F('answer_comment_count'),
        popular_score=ExpressionWrapper(
            F('vote_count') * 5 + F('answer_count') * 3 + F('comment_count') + F('view_count'),
            output_field=IntegerField(),
        ),
    ).order_by('-popular_score', '-create_date')[:10]

    context = {'question_list': question_list}
    return render(request, 'pybo/popular_question_list.html', context)


def detail(request, question_id):
    """
    pybo 내용 출력
    """
    question = get_object_or_404(Question, pk=question_id)
    viewed_question_ids = request.session.get('viewed_question_ids', [])
    question_key = str(question_id)
    if question_key not in viewed_question_ids:
        Question.objects.filter(pk=question_id).update(view_count=F('view_count') + 1)
        question.refresh_from_db(fields=['view_count'])
        viewed_question_ids.append(question_key)
        request.session['viewed_question_ids'] = viewed_question_ids
    context = {'question': question}
    return render(request, 'pybo/question_detail.html', context)
