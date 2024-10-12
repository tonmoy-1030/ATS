from django.shortcuts import redirect
from django.conf import settings
from django.urls import resolve

class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # List of URLs that do not require authentication (e.g., login, sign up)
        exempt_urls = [
            'login',  # Add the name of the login URL or any other public URL
            'home',
       
        ]

        # Get the name of the current view
        current_url = resolve(request.path_info).url_name

        # If the user is not authenticated and the current URL is not exempt, redirect to login
        if not request.user.is_authenticated and current_url not in exempt_urls:
            return redirect(f"{settings.LOGIN_URL}?next={request.path}")

        # Continue processing the request
        response = self.get_response(request)
        return response
