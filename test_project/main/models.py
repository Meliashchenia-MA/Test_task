from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    bio = models.TextField(default='', max_length=100, blank=True)
    request_count = models.IntegerField(default=0)

    def __str__(self):
        return self.username


class UploadModel(models.Model):
    user = models.ForeignKey('main.User', on_delete=models.CASCADE)
    original_image = models.ImageField(upload_to='images')
    processed_image = models.ImageField(upload_to='images')
    created_at = models.DateTimeField(auto_now_add=True)

