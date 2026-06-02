from django.utils import timezone

from .models import Notification


def create_notification(recipient, actor, notification_type, message, question=None, answer=None, comment=None):
    if recipient == actor:
        return None

    return Notification.objects.create(
        recipient=recipient,
        actor=actor,
        notification_type=notification_type,
        question=question,
        answer=answer,
        comment=comment,
        message=message,
        create_date=timezone.now(),
    )
