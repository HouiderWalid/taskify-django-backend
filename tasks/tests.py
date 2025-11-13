from django.test import TestCase
from datetime import datetime, timedelta

import jwt
from core import settings
from projects.models import Project
from tasks.models import Task
from users.models import Role, User
from django.core.management import call_command


class TaskTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        call_command('seed', verbosity=0)

    project = None

    def setUp(self):
        role = Role.objects.get(name=Role.MANAGER_ROLE)
        user = User.objects.create(
            full_name="project manager",
            email="projectmanager@example.com",
            password="projectmanagerpass",
            role=role
        )
        user.permissions.set(role.permissions.all())
        access_token = jwt.encode(
            {"user_id": user.id, "exp": datetime.now() + timedelta(minutes=15)}, settings.SECRET_KEY, algorithm="HS256"
        )
        self.client.defaults['HTTP_AUTHORIZATION'] = f'Bearer {access_token}'

        project_name = "Project for Task"
        project_description = "Project description"
        project_due_date = "2025-11-20 16:53:14"
        self.project = Project.objects.create(
            name=project_name,
            due_date=project_due_date,
            description=project_description,
            creator=User.objects.first()
        )

    def test_create_task(self):
        task_title = "Task 1"
        data = {
            "title": task_title,
            "description": "This is a sample task",
            "status": Task.IN_PROGRESS_STATUS,
            "priority": Task.HIGH_PRIORITY,
            "due_date": "2025-12-15 12:00:00",
            "project_id": self.project.id,
            "assigned_to_user_id": User.objects.first().id
        }
        response = self.client.post(
            '/api/task/', data, content_type='application/json')

        response_json = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_json['data']
                         ['data'][0]['title'], task_title)

    def test_update_task(self):
        task = Task.objects.create(
            project=self.project,
            title="Initial Task",
            description="Initial Description",
            due_date="2025-12-10 10:00:00"
        )

        updated_title = "Updated Task Title"
        data = {
            "title": updated_title,
            "description": "Updated Description",
            "status": Task.DONE_STATUS,
            "priority": Task.LOW_PRIORITY,
            "due_date": "2025-12-20 15:00:00",
            "project_id": self.project.id,
            "assigned_to_user_id": User.objects.first().id
        }
        response = self.client.put(
            f'/api/task/{task.id}/', data, content_type='application/json')

        response_json = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_json['data']
                         ['data'][0]['title'], updated_title)

    def test_delete_task(self):
        task = Task.objects.create(
            project=self.project,
            title="Task to be deleted",
            description="This task will be deleted",
            due_date="2025-12-10 10:00:00"
        )

        response = self.client.delete(f'/api/task/{task.id}/')

        self.assertEqual(response.status_code, 200)
        self.assertFalse(Task.objects.filter(id=task.id).exists())
