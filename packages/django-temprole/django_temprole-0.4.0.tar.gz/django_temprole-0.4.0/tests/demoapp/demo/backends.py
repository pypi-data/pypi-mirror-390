from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend


User = get_user_model()


class AnyUserAuthBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        user, __ = User.objects.update_or_create(
            username=username,
            defaults={
                "is_staff": True,
                "is_active": True,
                "is_superuser": username.startswith('admin'),
                "email": f'{username}@demo.org',
            },
        )
        return user
