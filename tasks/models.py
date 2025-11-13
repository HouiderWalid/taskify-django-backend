from django.db import models
from projects.models import Project
from users.models import User


class Task(models.Model):

    TODO_STATUS = 'todo'
    IN_PROGRESS_STATUS = 'in_progress'
    DONE_STATUS = 'done'

    LOW_PRIORITY = 'low'
    MEDIUM_PRIORITY = 'medium'
    HIGH_PRIORITY = 'high'

    STATUS_CHOICES = [
        (TODO_STATUS, 'To Do'),
        (IN_PROGRESS_STATUS, 'In Progress'),
        (DONE_STATUS, 'Done'),
    ]

    PRIORITY_CHOICES = [
        (LOW_PRIORITY, 'Low'),
        (MEDIUM_PRIORITY, 'Medium'),
        (HIGH_PRIORITY, 'High'),
    ]

    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name='tasks')
    assign_to_user = models.ForeignKey(
        User, on_delete=models.SET_NULL, related_name='tasks', null=True, blank=True)
    title = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    status = models.CharField(
        default=TODO_STATUS, choices=STATUS_CHOICES, max_length=20)
    priority = models.CharField(
        default=MEDIUM_PRIORITY, choices=PRIORITY_CHOICES, max_length=20)
    due_date = models.DateTimeField(null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    @staticmethod
    def get_statuses():
        return [Task.TODO_STATUS, Task.IN_PROGRESS_STATUS, Task.DONE_STATUS]

    @staticmethod
    def get_priorities():
        return [Task.LOW_PRIORITY, Task.MEDIUM_PRIORITY, Task.HIGH_PRIORITY]

    class Meta:
        db_table = 'tasks'
