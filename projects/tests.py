import json
from django.test import TestCase
from django.core.management import call_command
import jwt
from datetime import datetime, timedelta

from core import settings
from projects.models import Project
from users.models import Role, User


class ProjectTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        call_command('seed', verbosity=0)

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

    def test_project_creation(self):
        project_name = "Project 1"
        data = {
            "name": project_name,
            "due_date": "2025-11-20 16:53:14",
            "description": "This is a sample project"
        }
        response = self.client.post(
            '/api/project/', data, content_type='application/json')

        response_json = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_json['data']
                         ['data'][0]['name'], project_name)

    def test_project_updating(self):
        project = Project.objects.create(
            name="Initial Project",
            due_date="2025-12-31 23:59:59",
            description="Initial description",
            creator=User.objects.first()
        )

        updated_name = "Updated Project Name"
        data = {
            "name": updated_name,
            "due_date": "2026-01-31 23:59:59",
            "description": "Updated description"
        }

        response = self.client.put(
            f'/api/project/{project.id}/', data, content_type='application/json')

        response_json = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_json['data']
                         ['data'][0]['name'], updated_name)

    def test_project_deletion(self):
        project = Project.objects.create(
            name="Project to be deleted",
            due_date="2025-10-31 23:59:59",
            description="This project will be deleted",
            creator=User.objects.first()
        )

        response = self.client.delete(
            f'/api/project/{project.id}/', content_type='application/json')

        self.assertEqual(response.status_code, 200)
        self.assertFalse(Project.objects.filter(id=project.id).exists())
