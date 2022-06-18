from typing import Optional

from .models import Account


def user_exists_and_is_not_request_user(request, username) -> (Optional[Account], bool):
    try:
        account = Account.objects.get(username=username)
    except Account.DoesNotExist:
        return None, False
    if account == request.user:
        return None, False

    return account, True
