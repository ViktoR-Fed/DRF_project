from rest_framework import permissions, status
from rest_framework.generics import (CreateAPIView, DestroyAPIView,
                                     ListAPIView, RetrieveAPIView,
                                     UpdateAPIView)
from rest_framework.viewsets import ModelViewSet

from materials.models import Course, Lesson
from materials.serializers import (CourseDetailSerializer, CourseSerializer,
                                   LessonSerializer)

from .permissions import IsModerator, IsOwner


class CourseViewSet(ModelViewSet):
    queryset = Course.objects.all()

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
