from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()


class UserTests(APITestCase):
    """Простые тесты для пользователей"""

    def setUp(self):
        self.user = User.objects.create_user(
            email="test@test.com",
            password="test123",
            phone="+79991112233",
            city="Москва",
        )

    def test_register_password_mismatch(self):
        """Тест: ошибка при несовпадении паролей"""
        url = reverse("users:user_register")
        data = {
            "email": "new@test.com",
            "password": "test123",
            "password_confirm": "wrong",
            "phone": "+79998887766",
            "city": "СПб",
        }
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_profile_unauthenticated(self):
        """Тест: неавторизованный пользователь НЕ видит профиль"""
        url = reverse("users:user_profile")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_jwt_token(self):
        """Тест: получение JWT токена"""
        url = reverse("users:token")
        data = {"email": "test@test.com", "password": "test123"}
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_jwt_token_wrong_password(self):
        """Тест: ошибка при неверном пароле"""
        url = reverse("users:token")
        data = {"email": "test@test.com", "password": "wrong"}
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
