from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from materials.models import Course, Lesson
from users.models import Subscription

User = get_user_model()


class LessonCRUDTests(APITestCase):
    """Тесты для CRUD операций с уроками"""

    def setUp(self):
        # Создаем пользователей
        self.user = User.objects.create_user(
            email='user@test.com',
            password='test123'
        )

        self.another_user = User.objects.create_user(
            email='another@test.com',
            password='test123'
        )

        # Создаем курс и урок
        self.course = Course.objects.create(
            name='Тестовый курс',
            description='Описание',
            owner=self.user
        )

        self.lesson = Lesson.objects.create(
            name='Тестовый урок',
            description='Описание урока',
            video_link='https://www.youtube.com/watch?v=test',
            course=self.course,
            owner=self.user
        )

    def test_create_lesson(self):
        """Тест: авторизованный пользователь может создать урок"""
        self.client.force_authenticate(user=self.user)
        url = reverse('materials:lessons_create')
        data = {
            'name': 'Новый урок',  # name, а не title
            'description': 'Описание',
            'video_link': 'https://www.youtube.com/watch?v=new',
            'course': self.course.id
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Lesson.objects.count(), 2)

    def test_create_lesson_unauthenticated(self):
        """Тест: неавторизованный пользователь НЕ может создать урок"""
        url = reverse('materials:lessons_create')
        data = {
            'name': 'Новый урок',
            'video_link': 'https://www.youtube.com/watch?v=new',
            'course': self.course.id
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_lesson_invalid_youtube_link(self):
        """Тест: нельзя создать урок с ссылкой НЕ на YouTube"""
        self.client.force_authenticate(user=self.user)
        url = reverse('materials:lessons_create')
        data = {
            'name': 'Урок с плохой ссылкой',
            'video_link': 'https://example.com/video',
            'course': self.course.id
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('video_link', response.data)

    def test_update_lesson_owner(self):
        """Тест: владелец может обновить СВОЙ урок"""
        self.client.force_authenticate(user=self.user)
        url = reverse('materials:lessons_update', args=[self.lesson.id])
        data = {'name': 'Обновленный урок'}
        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.lesson.refresh_from_db()
        self.assertEqual(self.lesson.name, 'Обновленный урок')

    def test_delete_lesson_owner(self):
        """Тест: владелец может удалить СВОЙ урок"""
        self.client.force_authenticate(user=self.user)
        url = reverse('materials:lessons_delete', args=[self.lesson.id])
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Lesson.objects.count(), 0)

class SubscriptionTests(APITestCase):
    """Тесты для подписки на курсы"""

    def setUp(self):
        self.user = User.objects.create_user(
            email='user@test.com',
            password='test123'
        )

        self.another_user = User.objects.create_user(
            email='another@test.com',
            password='test123'
        )

        self.course = Course.objects.create(
            name='Курс для подписки',
            description='Описание',
            owner=self.user
        )

        self.another_course = Course.objects.create(
            name='Другой курс',
            description='Описание',
            owner=self.another_user
        )

    def test_subscribe_to_course(self):
        """Тест: пользователь может подписаться на курс"""
        self.client.force_authenticate(user=self.another_user)
        url = reverse('materials:subscription')
        data = {'course_id': self.course.id}
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Подписка добавлена')
        self.assertTrue(response.data['is_subscribed'])

        self.assertTrue(
            Subscription.objects.filter(
                user=self.another_user,
                course=self.course
            ).exists()
        )

    def test_unsubscribe_from_course(self):
        """Тест: пользователь может отписаться от курса"""
        # Сначала подписываемся
        Subscription.objects.create(user=self.another_user, course=self.course)

        self.client.force_authenticate(user=self.another_user)
        url = reverse('materials:subscription')
        data = {'course_id': self.course.id}
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Подписка удалена')
        self.assertFalse(response.data['is_subscribed'])

        self.assertFalse(
            Subscription.objects.filter(
                user=self.another_user,
                course=self.course
            ).exists()
        )

    def test_subscribe_toggle(self):
        """Тест: повторная подписка переключает статус (on/off)"""
        self.client.force_authenticate(user=self.another_user)
        url = reverse('materials:subscription')
        data = {'course_id': self.course.id}

        # Первый раз - подписываемся
        response1 = self.client.post(url, data, format='json')
        self.assertEqual(response1.data['message'], 'Подписка добавлена')

        # Второй раз - отписываемся
        response2 = self.client.post(url, data, format='json')
        self.assertEqual(response2.data['message'], 'Подписка удалена')

    def test_subscribe_unauthenticated(self):
        """Тест: неавторизованный пользователь НЕ может подписаться"""
        url = reverse('materials:subscription')
        data = {'course_id': self.course.id}
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_subscribe_nonexistent_course(self):
        """Тест: подписка на несуществующий курс"""
        self.client.force_authenticate(user=self.another_user)
        url = reverse('materials:subscription')
        data = {'course_id': 9999}
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_subscribe_without_course_id(self):
        """Тест: подписка без указания курса"""
        self.client.force_authenticate(user=self.another_user)
        url = reverse('materials:subscription')
        data = {}
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

