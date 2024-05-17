from django.db import models
from django.contrib.auth.models import AbstractUser

def user_directory_path(instance, filename):
    return f'user_images/{instance.user.username}/{filename}'


class User(AbstractUser):
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.username

class Image(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to=user_directory_path)  

    def __str__(self):
        return f"Image for {self.user.username}"
