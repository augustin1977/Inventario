from django.shortcuts import redirect
from django.contrib.auth import login

class ForcePasswordChangeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and request.user.last_login is None:
            return redirect('password_change')
        response = self.get_response(request)
        return response