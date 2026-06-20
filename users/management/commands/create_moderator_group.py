from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand

from materials.models import Course, Lesson


class Command(BaseCommand):
    help = "Создает группу модераторов с соответствующими правами"

    def handle(self, *args, **options):
        # Создаем группу
        group, created = Group.objects.get_or_create(name="Модераторы")

        if created:
            self.stdout.write(self.style.SUCCESS('Группа "Модераторы" создана'))
        else:
            self.stdout.write(self.style.WARNING('Группа "Модераторы" уже существует'))

        # Получаем разрешения для курсов и уроков
        course_ct = ContentType.objects.get_for_model(Course)
        lesson_ct = ContentType.objects.get_for_model(Lesson)

        # Разрешения для модераторов
        permissions = Permission.objects.filter(
            content_type__in=[course_ct, lesson_ct],
            codename__in=[
                "view_course",
                "change_course",
                "view_lesson",
                "change_lesson",
            ],
        )

        # Назначаем разрешения
        group.permissions.set(permissions)

        self.stdout.write(
            self.style.SUCCESS(
                f'Группе назначены разрешения: {", ".join([p.name for p in permissions])}'
            )
        )
