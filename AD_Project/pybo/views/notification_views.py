from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from ..models import Notification


@login_required(login_url='common:login')
def notification_list(request):
    page = request.GET.get('page', '1')
    notifications = request.user.notifications.select_related(
        'actor',
        'question',
        'answer__question',
        'comment__question',
        'comment__answer__question',
    )

    paginator = Paginator(notifications, 10)
    page_obj = paginator.get_page(page)

    context = {'notification_list': page_obj}
    return render(request, 'pybo/notification_list.html', context)


@require_POST
@login_required(login_url='common:login')
def notification_read(request, notification_id):
    notification = get_object_or_404(
        Notification,
        pk=notification_id,
        recipient=request.user,
    )
    if notification.read_date is None:
        notification.read_date = timezone.now()
        notification.save(update_fields=['read_date'])

    target_question_id = notification.target_question_id
    if target_question_id:
        return redirect('pybo:detail', question_id=target_question_id)
    return redirect('pybo:notification_list')
