from django.db import models

# Create your models here.
class User(models.Model):
    email = models.CharField(max_length=50, default="", unique=True)
    password = models.CharField(max_length=50, default="")
    name = models.CharField(max_length=50, default="")
    surname = models.CharField(max_length=50, default="")
    created_at = models.DateTimeField(auto_now_add=True)

