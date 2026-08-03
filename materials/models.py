from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Course(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name="Название курса",
        help_text="Укажите название курса",
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name="Описание курса",
        help_text="Укажите описание курса",
    )
    preview = models.ImageField(
        upload_to="course_previews/",
        blank=True,
        null=True,
        verbose_name="Превью (картинка)",
    )
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="courses",
        verbose_name="Владелец",
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Дата создания", null=True, blank=True
    )
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name="Дата обновления", null=True, blank=True
    )

    class Meta:
        verbose_name = "Курс"
        verbose_name_plural = "Курсы"

    def __str__(self):
        return self.name


class Lesson(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name="Название урока",
        help_text="Укажите название урока",
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name="Описание урока",
        help_text="Укажите описание урока",
    )
    preview = models.ImageField(
        upload_to="lesson_previews/",
        blank=True,
        null=True,
        verbose_name="Превью (картинка)",
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="lessons",
        verbose_name="Курс",
        blank=True,
        null=True,
    )
    video_link = models.URLField(verbose_name="Ссылка на видео", blank=True, null=True)
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="lessons",
        verbose_name="Владелец",
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Дата создания", null=True, blank=True
    )
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name="Дата обновления", null=True, blank=True
    )

    class Meta:
        verbose_name = "Урок"
        verbose_name_plural = "Уроки"

    def __str__(self):
        return f"{self.name} (курс: {self.course.name})"
