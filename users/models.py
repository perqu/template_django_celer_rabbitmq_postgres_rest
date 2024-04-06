import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth.models import Group

class User(AbstractUser):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    password = models.CharField(max_length=128, blank=False)

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        return self.username
