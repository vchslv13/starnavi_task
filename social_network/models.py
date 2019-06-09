from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import fields


class User(AbstractUser):
    first_name = None
    last_name = None
    email = fields.EmailField(unique=True)
    full_name = fields.CharField(max_length=250)
