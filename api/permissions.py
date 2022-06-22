from rest_framework import permissions

from users.models import Account
from follow.models import Following

class FollowingPrivatePermission(permissions.BasePermission):
    """Check if request user follows private account they're trying to access."""
    message = 'This account is private and you are not following it.'

    def has_permission(self, request, view):
        other_user = Account.objects.get(username=view.kwargs.get('username'))
        if not other_user.is_public:
            following_users = Following.objects.get(user=request.user).users_following.all()
            return other_user in following_users
        return True