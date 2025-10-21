from django.contrib import admin
from .models import Task, News

# Register your models here.

admin.site.register(Task)
admin.site.register(News)