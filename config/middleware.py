from django.conf import settings
from django.http import HttpResponseRedirect
from django.urls import resolve, reverse
from django.utils.deprecation import MiddlewareMixin


class LoginRequiredMiddleware(MiddlewareMixin):
    """
    Middleware that requires a user to be authenticated to
    view any page other than AUTH_EXEMPT_ROUTES.
    """

    def process_request(self, request):
        assert hasattr(request, 'user')
        current_route = resolve(request.path_info).url_name

        if request.user.is_authenticated:
            if current_route in settings.AUTH_ROUTES:
                return HttpResponseRedirect(reverse(settings.AUTH_REDIRECT))

        if not request.user.is_authenticated:
            if current_route not in settings.AUTH_EXEMPT_ROUTES:
                return HttpResponseRedirect(reverse(settings.AUTH_LOGIN_ROUTE))