from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import fields
from django.db.models.fields.related import ForeignKey, ManyToManyField
from django.utils import timezone


class User(AbstractUser):
    first_name = None
    last_name = None
    email = fields.EmailField(unique=True)
    full_name = fields.CharField(max_length=250)
    is_active = fields.BooleanField(default=False)


class Post(models.Model):
    creation_datetime = fields.DateTimeField(default=timezone.now)
    text = fields.TextField(max_length=5000)
    author = ForeignKey(User, on_delete=models.CASCADE)
    liked_by_users = ManyToManyField(User, related_name='liked_posts')
