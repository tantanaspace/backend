import datetime

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from apps.users.models import User

LOGIN_URLS = {
    'login': reverse("api:shared_v1:login"),
}


class LoginTestCase(APITestCase):
    def setUp(self):
        self.existing_user_data = {
            "phone_number": "+998901234567",
            "password": "12345678",
            "date_of_birth": datetime.date(1999, 12, 31),
            "full_name": "Adam Sandler",
        }

    def tearDown(self):
        User.objects.all().delete()

    def given_existing_user(self) -> User:
        user = User.objects.create_user(**self.existing_user_data)
        return user

    def test_user_doesnt_exist_fails_login(self):
        data = {
            "phone_number": "+998901234567",
            "password": "Non existing password",
        }

        response = self.client.post(LOGIN_URLS['login'], data=data)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_successful_login(self):
        self.given_existing_user()
        data = {
            "phone_number": self.existing_user_data.get("phone_number"),
            "password": self.existing_user_data.get("password"),
        }
        response = self.client.post(LOGIN_URLS['login'], data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_wrong_password(self):
        self.given_existing_user()
        data = {
            "phone_number": self.existing_user_data.get("phone_number"),
            "password": "WRONG PASSWORD",
        }
        response = self.client.post(LOGIN_URLS['login'], data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
