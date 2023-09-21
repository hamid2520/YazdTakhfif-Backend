from django.db import models


class Advertise(models.Model):
    file = models.FileField(upload_to="advertise/")
    link = models.URLField()
