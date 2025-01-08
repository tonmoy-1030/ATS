from django.shortcuts import redirect
from django.conf import settings
from django.urls import resolve

class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # List of URLs that do not require authentication
        exempt_urls = ['login', 'unauthorized', 'logout']  # Add other public URLs here

        # Define user-specific accessible URLs
        user_specific_urls = {
            'guest': ['daily_joining', 'daily_joining_update', 'daily_joining_delete', 'daily_joining_list'],
            'gbml-bagerhat-hr': ['daily_joining', 'daily_joining_update', 'daily_joining_delete', 'daily_joining_list'],
            'gbml-bogura-hr': ['daily_joining', 'daily_joining_update', 'daily_joining_delete', 'daily_joining_list'],
            'gbml-jashore-hr': ['daily_joining', 'daily_joining_update', 'daily_joining_delete', 'daily_joining_list'],
            'gbml-rangpur-hr': ['daily_joining', 'daily_joining_update', 'daily_joining_delete', 'daily_joining_list'],
            'ppl-pcl-hr': ['daily_joining', 'daily_joining_update', 'daily_joining_delete', 'daily_joining_list'],
            'sfll-hr': ['daily_joining', 'daily_joining_update', 'daily_joining_delete', 'daily_joining_list'],
            'sorl-hr': ['daily_joining', 'daily_joining_update', 'daily_joining_delete', 'daily_joining_list'],
            'svoil-hr': ['daily_joining', 'daily_joining_update', 'daily_joining_delete', 'daily_joining_list'],
            'food-comilla-hr': ['daily_joining', 'daily_joining_update', 'daily_joining_delete', 'daily_joining_list'],
            'food-dhamrai-hr': ['daily_joining', 'daily_joining_update', 'daily_joining_delete', 'daily_joining_list'],
            'food-gazipur-hr': ['daily_joining', 'daily_joining_update', 'daily_joining_delete', 'daily_joining_list'],
            'food-narsigdi-hr': ['daily_joining', 'daily_joining_update', 'daily_joining_delete', 'daily_joining_list'],
            'food-potiya-hr': ['daily_joining', 'daily_joining_update', 'daily_joining_delete', 'daily_joining_list'],
            
            
            # Add more users and their allowed URLs
        }

        # Get the name of the current view
        current_url = resolve(request.path_info).url_name

        # Check if the user is authenticated
        if not request.user.is_authenticated:
            if current_url not in exempt_urls:
                return redirect(f"{settings.LOGIN_URL}?next={request.path}")

        # Restrict access for users explicitly defined in the list
        if request.user.is_authenticated:
            if request.user.username in user_specific_urls:
                allowed_urls = user_specific_urls[request.user.username]
                if current_url not in exempt_urls and current_url not in allowed_urls:
                    return redirect('report:daily_joining_list')  # Redirect to an unauthorized access page

        # If the user is not in the user-specific list, allow access to all URLs
        response = self.get_response(request)
        return response
