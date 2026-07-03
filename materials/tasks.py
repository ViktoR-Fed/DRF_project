from datetime import datetime, timedelta

from celery import shared_task
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail

from .models import Course, Lesson

User = get_user_model()


@shared_task
def send_course_update_notification(course_id, user_email, course_name):
    """
    Отправка уведомления пользователю об обновлении курса
    """
    subject = f"Обновление курса: {course_name}"
    message = f"""
    Здравствуйте!

    Курс "{course_name}" был обновлен.
    Новые материалы уже доступны для изучения.

    Перейдите по ссылке, чтобы ознакомиться с обновлениями:
    http://localhost:8000/courses/{course_id}/

    С уважением,
    Команда проекта
    """

    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user_email],
            fail_silently=False,
        )
        return f"Письмо отправлено пользователю {user_email}"
    except Exception as e:
        return f"Ошибка отправки письма: {str(e)}"


@shared_task
def notify_course_subscribers(course_id, last_update_time=None):
    """
    Уведомление всех подписчиков курса об обновлении
    """
    from users.models import Subscription

    try:
        course = Course.objects.get(id=course_id)

        # Проверяем, обновлялся ли курс недавно
        if last_update_time:
            time_since_update = datetime.now() - last_update_time
            if time_since_update < timedelta(hours=4):
                return f"Курс {course.name} обновлялся менее 4 часов назад. Уведомление отложено"

        # Получаем всех подписчиков курса
        subscriptions = Subscription.objects.filter(course=course).select_related(
            "user"
        )

        if not subscriptions.exists():
            return f"Нет подписчиков у курса {course.name}"

        # Отправляем уведомления всем подписчикам
        for subscription in subscriptions:
            user = subscription.user
            if user.email:
                send_course_update_notification.delay(
                    course_id=course.id, user_email=user.email, course_name=course.name
                )

        return f"Уведомления отправлены {subscriptions.count()} подписчикам курса {course.name}"

    except Course.DoesNotExist:
        return f"Курс с ID {course_id} не найден"
    except Exception as e:
        return f"Ошибка: {str(e)}"


@shared_task
def send_lesson_update_notification(lesson_id, user_email, lesson_name, course_name):
    """
    Отправка уведомления об обновлении урока
    """
    subject = f"Обновление урока: {lesson_name}"
    message = f"""
    Здравствуйте!

    Урок "{lesson_name}" в курсе "{course_name}" был обновлен.

    Перейдите по ссылке, чтобы ознакомиться с обновлениями:
    http://localhost:8000/lessons/{lesson_id}/

    С уважением,
    Команда проекта
    """

    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user_email],
            fail_silently=False,
        )
        return f"Письмо отправлено пользователю {user_email}"
    except Exception as e:
        return f"Ошибка отправки письма: {str(e)}"
