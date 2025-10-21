from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class News(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    date = models.DateField()
    url = models.URLField()

    def __str__(self):
        return f"news about {self.title} by {self.url}"
    
class Task(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    status = models.CharField(max_length=50, choices=[('Pending', 'Pending'), ('Done', 'Done')])
    description = models.TextField(blank=True, null=True)
    date = models.DateField()
    time = models.TimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"task about {self.title} by {self.user}"
    

class FocusSession(models.Model):
    started_at = models.DateTimeField(auto_now_add=True)
    duration_minutes = models.IntegerField(default=25)
    completed = models.BooleanField(False)
    