from django.db import models

from src.users.models import User


class Business(models.Model):
    title = models.CharField(max_length=128, unique=True)
    user = models.OneToOneField(to=User, on_delete=models.CASCADE)

    def __str__(self):
        return self.title.capitalize()
