from django.db import models
from src.config import common


class Business(models.Model):
    name = models.CharField(max_length=128)
    user = models.ForeignKey(to=common.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Operator(models.Model):
    business = models.ForeignKey(to=Business, on_delete=models.CASCADE)
    user = models.ForeignKey(to=common.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user}({self.business})"
