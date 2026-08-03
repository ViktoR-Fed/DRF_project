from django.core.management.base import BaseCommand

from users.tasks import block_inactive_users


class Command(BaseCommand):
    help = "Блокирует пользователей, не заходивших более месяца"

    def handle(self, *args, **options):
        self.stdout.write("Запуск задачи блокировки неактивных пользователей...")

        result = block_inactive_users.delay()

        self.stdout.write(self.style.SUCCESS(f"Задача запущена (ID: {result.id})"))
        self.stdout.write("Проверьте результат в журнале Celery")
