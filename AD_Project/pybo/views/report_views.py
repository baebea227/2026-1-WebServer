from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.db import IntegrityError
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from ..forms import ContentReportForm, ContentReportReviewForm
from ..models import Answer, Comment, ContentReport, Question


def _get_report_target(target_type, target_id):
    if target_type == 'question':
        target = get_object_or_404(Question, pk=target_id)
        return target, {'question': target}, target.id, '질문'
    if target_type == 'answer':
        target = get_object_or_404(Answer, pk=target_id)
        return target, {'answer': target}, target.question_id, '답변'
    if target_type == 'comment':
        target = get_object_or_404(Comment, pk=target_id)
        question_id = target.question_id or target.answer.question_id
        return target, {'comment': target}, question_id, '댓글'
    raise ValueError('지원하지 않는 신고 대상입니다.')


def _staff_required(user):
    return user.is_authenticated and user.is_staff


@login_required(login_url='common:login')
def report_create(request, target_type, target_id):
    try:
        target, target_fields, question_id, target_label = _get_report_target(target_type, target_id)
    except ValueError:
        messages.error(request, '지원하지 않는 신고 대상입니다.')
        return redirect('pybo:index')

    if target.author == request.user:
        messages.error(request, '본인이 작성한 콘텐츠는 신고할 수 없습니다.')
        return redirect('pybo:detail', question_id=question_id)

    duplicate_report = ContentReport.objects.filter(
        reporter=request.user,
        target_type=target_type,
        target_object_id=target.id,
    ).exists()
    if duplicate_report:
        messages.error(request, '이미 신고한 콘텐츠입니다.')
        return redirect('pybo:detail', question_id=question_id)

    if request.method == 'POST':
        form = ContentReportForm(request.POST)
        for field, value in target_fields.items():
            setattr(form.instance, field, value)
        if form.is_valid():
            report = form.save(commit=False)
            report.reporter = request.user
            report.create_date = timezone.now()
            try:
                report.save()
            except IntegrityError:
                messages.error(request, '이미 신고한 콘텐츠입니다.')
                return redirect('pybo:detail', question_id=question_id)
            messages.success(request, '신고가 접수되었습니다.')
            return redirect('pybo:detail', question_id=question_id)
    else:
        form = ContentReportForm()

    context = {
        'form': form,
        'target': target,
        'target_label': target_label,
        'question_id': question_id,
    }
    return render(request, 'pybo/report_form.html', context)


@user_passes_test(_staff_required, login_url='common:login')
def report_list(request):
    status = request.GET.get('status', '')
    report_list = ContentReport.objects.select_related(
        'reporter',
        'reviewed_by',
        'question',
        'answer',
        'answer__question',
        'comment',
        'comment__question',
        'comment__answer',
        'comment__answer__question',
    )
    if status:
        report_list = report_list.filter(status=status)

    paginator = Paginator(report_list, 10)
    page_obj = paginator.get_page(request.GET.get('page', '1'))
    context = {
        'report_list': page_obj,
        'status': status,
        'status_choices': ContentReport.STATUS_CHOICES,
    }
    return render(request, 'pybo/report_list.html', context)


@user_passes_test(_staff_required, login_url='common:login')
def report_detail(request, report_id):
    report = get_object_or_404(
        ContentReport.objects.select_related(
            'reporter',
            'reviewed_by',
            'question',
            'answer',
            'answer__question',
            'comment',
            'comment__question',
            'comment__answer',
            'comment__answer__question',
        ),
        pk=report_id,
    )
    if request.method == 'POST':
        form = ContentReportReviewForm(request.POST, instance=report)
        if form.is_valid():
            report = form.save(commit=False)
            report.reviewed_by = request.user
            report.reviewed_at = timezone.now()
            report.save()
            messages.success(request, '신고 검토 결과가 저장되었습니다.')
            return redirect('pybo:report_detail', report_id=report.id)
    else:
        form = ContentReportReviewForm(instance=report)

    context = {
        'form': form,
        'report': report,
    }
    return render(request, 'pybo/report_detail.html', context)
