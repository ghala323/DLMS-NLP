from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings


class CustomUser(AbstractUser):

    email = models.EmailField(unique=True)

    national_id = models.CharField(max_length=20, unique=True)

    USERNAME_FIELD = 'national_id'

    REQUIRED_FIELDS = ['email','username']

    def __str__(self):

        return self.national_id


class Profile(models.Model):

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    phone_number = models.CharField(max_length=15, unique=True)

    def __str__(self):

        return self.user.national_id