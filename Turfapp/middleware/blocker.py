from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse
from django.contrib.auth import logout

class BlockedUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            if getattr(request.user, "is_blocked", False):  # check custom field
                logout(request)
                messages.error(request, "Your account has been blocked. Contact support.")
                return redirect(reverse("login"))  # make sure "login" is your URL name

        return self.get_response(request)
