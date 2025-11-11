from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission, Group
from factory import SubFactory, Sequence, LazyFunction, post_generation, PostGenerationMethodCall
from factory.django import DjangoModelFactory
from django.utils import timezone
from datetime import timedelta

from django_temprole.models import TemporaryRole


class UserFactory(DjangoModelFactory):
    username = Sequence(lambda n: f"test_user_{n}")
    email = Sequence(lambda n: f"test_user_{n}@nomail.com")
    password = PostGenerationMethodCall("set_password", "testpassword123")

    class Meta:
        model = get_user_model()
        django_get_or_create = ("username",)


class GroupFactory(DjangoModelFactory):
    name = Sequence(lambda n: f"test_group_{n}")

    class Meta:
        model = Group
        skip_postgeneration_save = True

    @post_generation
    def permissions(self, create, extracted, **kwargs):
        if not create:
            return

        # Check if extracted is a list/iterable (not None and not the manager itself)
        if extracted is not None and not hasattr(extracted, "add"):
            # extracted is a list of permissions passed in
            for perm in extracted:
                self.permissions.add(perm)
        else:
            # No permissions passed, create a default one
            self.permissions.add(Permission.objects.filter(codename="view_user").first())


class TemporaryRoleFactory(DjangoModelFactory):
    user = SubFactory(UserFactory)

    # by default an active temporary permission
    start_datetime = LazyFunction(lambda: timezone.now() - timedelta(minutes=4))
    end_datetime = LazyFunction(lambda: timezone.now() + timedelta(days=5))
    group = LazyFunction(lambda: GroupFactory())

    class Meta:
        model = TemporaryRole
