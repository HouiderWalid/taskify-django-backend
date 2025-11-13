from django.db import models
from users.models import User


class Project(models.Model):
    creator = models.ForeignKey(
        User, on_delete=models.SET_NULL, related_name='projects', null=True, blank=True)
    name = models.CharField(max_length=255, null=False)
    due_date = models.DateTimeField(null=True, blank=False)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'projects'
