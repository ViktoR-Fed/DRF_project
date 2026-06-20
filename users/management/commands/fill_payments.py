from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from materials.models import Course, Lesson
from users.models import Payment

User = get_user_model()


class Command(BaseCommand):
    help = "Заполняет таблицу платежей тестовыми данными"

    def handle(self, *args, **options):
        user1 = User.objects.first()
        course1 = Course.objects.first()
        lesson1 = Lesson.objects.first()

        payments_data = [
            {
                "user": user1,
                "paid_course": course1,
                "paid_lesson": None,
                "amount": 4999.00,
                "payment_method": "transfer",
            },
            {
                "user": user1,
                "paid_course": None,
                "paid_lesson": lesson1,
                "amount": 999.00,
                "payment_method": "cash",
            },
        ]

        for data in payments_data:
            Payment.objects.get_or_create(**data)

        self.stdout.write(self.style.SUCCESS("Платежи успешно добавлены"))
