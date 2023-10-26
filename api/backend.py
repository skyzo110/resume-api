from django.contrib.auth.backends import ModelBackend
from .models import User  # Replace 'your_app' and 'YourUserModel' with your actual app and user model

class EmailBackend(ModelBackend):
    def authenticate(self, request, email=None, password=None, **kwargs):
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return None
        if user.check_password(password):
            return user
