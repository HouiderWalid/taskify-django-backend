from django.test import TestCase
from django.core.management import call_command
import jwt
from core import settings
from users.models import User
from django.contrib.auth.hashers import make_password
from datetime import datetime, timedelta


class UserTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        call_command('seed', verbosity=0)

    def test_signup(self):

        email = "member@example.com"
        data = {
            "full_name": "member user",
            "email": email,
            "password": "123456789"
        }

        response = self.client.post(
            '/api/signup/', data, content_type='application/json')

        response_json = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertTrue(User.objects.filter(email=email).exists())
        self.assertIn('token', response_json['data'])
        self.assertIn('user', response_json['data'])

    def test_signin(self):

        full_name = "member 2"
        email = "member2@example.com"
        password = "member2pass"

        User.objects.create(
            full_name=full_name,
            email=email,
            password=make_password(password)
        )

        data = {
            "email": email,
            "password": password
        }

        response = self.client.post(
            '/api/signin/', data, content_type='application/json')

        response_json = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertIn('token', response_json['data'])
        self.assertIn('user', response_json['data'])

    def test_authentication(self):

        full_name = "member 3"
        email = "member3@example.com"
        password = "member3pass"

        user = User.objects.create(
            full_name=full_name,
            email=email,
            password=make_password(password)
        )

        access_token = jwt.encode(
            {"user_id": user.id, "exp": datetime.now() + timedelta(minutes=15)}, settings.SECRET_KEY, algorithm="HS256"
        )

        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        response = self.client.get(
            '/api/auth_data/', headers=headers)

        response_json = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_json['data']['email'], email)
