from datetime import timedelta

from celery import shared_task
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


@shared_task
def block_inactive_users():
    """
    Блокировка пользователей, которые не заходили более месяца
    """
    try:
        # Рассчитываем дату месяц назад
        one_month_ago = timezone.now() - timedelta(days=30)

        # Находим активных пользователей, которые не заходили более месяца
        inactive_users = User.objects.filter(
            is_active=True, last_login__lt=one_month_ago
        )

        count = inactive_users.count()

        if count > 0:
            # Блокируем пользователей
            inactive_users.update(is_active=False)

            # Логируем результат
            result = f"Заблокировано {count} неактивных пользователей"

            return result
        else:
            return "Нет пользователей для блокировки"

    except Exception as e:
        return f"Ошибка при блокировке пользователей: {str(e)}"


@shared_task
def check_user_activity(user_id):
    """
    Проверка активности конкретного пользователя
    """
    try:
        user = User.objects.get(id=user_id)
        one_month_ago = timezone.now() - timedelta(days=30)

        if user.last_login and user.last_login < one_month_ago:
            user.is_active = False
            user.save()
            return f"Пользователь {user.email} заблокирован за неактивность"
        return f"Пользователь {user.email} активен"
    except User.DoesNotExist:
        return f"Пользователь с ID {user_id} не найден"
