from django.contrib import admin
from .models import User, Image

# Register your models here.


class UserAdmin(admin.ModelAdmin):
    pass


class ImageAdmin(admin.ModelAdmin):
    pass



admin.site.register(User, UserAdmin)
admin.site.register(Image, ImageAdmin)