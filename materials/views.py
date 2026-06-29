from rest_framework import permissions, status
from rest_framework.generics import (CreateAPIView, DestroyAPIView,
                                     ListAPIView, RetrieveAPIView,
                                     UpdateAPIView)
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from materials.models import Course, Lesson
from materials.serializers import (CourseDetailSerializer, CourseSerializer,
                                   LessonSerializer)
from users.models import Subscription
from django.shortcuts import get_object_or_404

from .paginators import CoursePaginator, LessonPaginator
from .permissions import IsModerator, IsOwner


class CourseViewSet(ModelViewSet):
    queryset = Course.objects.all()
    pagination_class = CoursePaginator
    def get_serializer_class(self):
        if self.action == "retrieve":
            return CourseDetailSerializer
        return CourseSerializer

    def get_permissions(self):
        """
        Разграничение прав доступа для разных действий
        """
        if self.action in ["list", "retrieve"]:
            # Просмотр доступен всем авторизованным
            self.permission_classes = [permissions.IsAuthenticated]
        elif self.action in ["create"]:
            # Создание доступно только НЕ модераторам
            self.permission_classes = [permissions.IsAuthenticated, ~IsModerator]
        elif self.action in ["update", "partial_update"]:
            # Редактирование доступно модераторам ИЛИ владельцам
            self.permission_classes = [
                permissions.IsAuthenticated,
                IsModerator | IsOwner,
            ]
        elif self.action in ["destroy"]:
            # Удаление доступно только владельцам
            self.permission_classes = [permissions.IsAuthenticated, IsOwner]
        return super().get_permissions()

    def perform_create(self, serializer):
        """Автоматически привязываем владельца при создании"""
        serializer.save(owner=self.request.user)

    def get_queryset(self):
        """Фильтрация объектов в зависимости от прав"""
        user = self.request.user

        if user.is_staff:
            return Course.objects.all()

        if user.groups.filter(name="Модераторы").exists():
            return Course.objects.all()

        # Обычные пользователи видят только свои курсы
        return Course.objects.filter(owner=user)


class LessonCreateApiview(CreateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    pagination_class = LessonPaginator

class LessonListApiview(ListAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer


class LessonRetrieveApiView(RetrieveAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer


class LessonUpdateApiView(UpdateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer


class LessonDestroyApiView(DestroyAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer


class LessonViewSet(ModelViewSet):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer

    def get_permissions(self):
        """
        Разграничение прав доступа для разных действий
        """
        if self.action in ["list", "retrieve"]:
            # Просмотр доступен всем авторизованным
            self.permission_classes = [permissions.IsAuthenticated]
        elif self.action in ["create"]:
            # Создание доступно только НЕ модераторам
            self.permission_classes = [permissions.IsAuthenticated, ~IsModerator]
        elif self.action in ["update", "partial_update"]:
            # Редактирование доступно модераторам ИЛИ владельцам
            self.permission_classes = [
                permissions.IsAuthenticated,
                IsModerator | IsOwner,
            ]
        elif self.action in ["destroy"]:
            # Удаление доступно только владельцам
            self.permission_classes = [permissions.IsAuthenticated, IsOwner]
        return super().get_permissions()

    def perform_create(self, serializer):
        """Автоматически привязываем владельца при создании"""
        serializer.save(owner=self.request.user)

    def get_queryset(self):
        """Фильтрация объектов в зависимости от прав"""
        user = self.request.user

        if user.is_staff:
            return Lesson.objects.all()

        if user.groups.filter(name="Модераторы").exists():
            return Lesson.objects.all()

        # Обычные пользователи видят только свои уроки
        return Lesson.objects.filter(owner=user)


class SubscriptionView(APIView):
    """
    Эндпоинт для управления подписками на курс
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        course_id = request.data.get('course_id')

        if not course_id:
            return Response(
                {"error": "Не указан ID курса"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Получаем курс или возвращаем 404
        course = get_object_or_404(Course, id=course_id)

        # Проверяем, существует ли подписка
        subscription = Subscription.objects.filter(
            user=user,
            course=course
        )

        if subscription.exists():
            # Если подписка есть - удаляем
            subscription.delete()
            message = "Подписка удалена"
            subscribed = False
        else:
            # Если подписки нет - создаем
            Subscription.objects.create(user=user, course=course)
            message = "Подписка добавлена"
            subscribed = True

        return Response({
            "message": message,
            "is_subscribed": subscribed,
            "course_id": course.id,
            "course_name": course.name
        }, status=status.HTTP_200_OK)

    def get(self, request):
        """Получить список подписок пользователя"""
        user = request.user
        subscriptions = Subscription.objects.filter(user=user).select_related('course')

        data = [{
            'course_id': sub.course.id,
            'course_name': sub.course.name,
            'created_at': sub.created_at
        } for sub in subscriptions]

        return Response(data, status=status.HTTP_200_OK)

