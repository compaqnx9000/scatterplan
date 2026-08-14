from django.contrib.auth.models import AbstractUser
from django.db import models


# Create your models here.
class CustomUser(AbstractUser):
    description = models.TextField(blank=True, null=True)  # 描述

    def __str__(self):
        return self.username
