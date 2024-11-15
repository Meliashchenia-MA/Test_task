from django.contrib import admin
from .models import UploadModel, User


class UploadModelAdmin(admin.ModelAdmin):
    list_display = ('user', 'original_image', 'processed_image', 'created_at')


admin.site.register(UploadModel)
admin.site.register(User)