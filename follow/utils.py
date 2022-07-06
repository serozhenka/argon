from django.conf import settings
from typing import Optional

from users.models import Account
from notifications.models import Notification

def user_exists_and_is_not_request_user(request, username) -> (Optional[Account], bool):
    try:
        account = Account.objects.get(username=username)
    except Account.DoesNotExist:
        return None, False
    if account == request.user:
        return None, False

    return account, True


def clear_following_notifications(sender: settings.AUTH_USER_MODEL, receiver: settings.AUTH_USER_MODEL) -> list:
    """Method to clear previous following notification when new one is created."""

    notifications_to_delete = Notification.objects.filter(sender=sender, receiver=receiver, action_name="follow")
    notifications_to_delete_id_list = list(notifications_to_delete.values_list('id', flat=True))
    notifications_to_delete.delete()

    return notifications_to_delete_id_list


def clear_fr_notifications(sender: settings.AUTH_USER_MODEL, receiver: settings.AUTH_USER_MODEL) -> list:
    """
        Method to clear previous following request notifications
        when new following action is initialized.
    """
    notifications_to_delete_id_list = []

    notifications_to_delete = Notification.objects.filter(sender=receiver, receiver=sender, action_name="send_fr")
    notifications_to_delete_id_list.extend(list(notifications_to_delete.values_list('id', flat=True)))
    notifications_to_delete.delete()

    notifications_to_delete = Notification.objects.filter(
        sender=sender,
        receiver=receiver,
        action_name__in=["accept_fr", "decline_fr"]
    )
    notifications_to_delete_id_list.extend(list(notifications_to_delete.values_list('id', flat=True)))
    notifications_to_delete.delete()

    return notifications_to_delete_id_list

def clear_send_fr_notifications(sender: settings.AUTH_USER_MODEL, receiver: settings.AUTH_USER_MODEL) -> list:
    notifications_to_delete = Notification.objects.filter(
        sender=sender,
        receiver=receiver,
        action_name__in=["send_fr", "follow"],
    )
    notifications_to_delete_id_list = list(notifications_to_delete.values_list('id', flat=True))
    notifications_to_delete.delete()

    return notifications_to_delete_id_list