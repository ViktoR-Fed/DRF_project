import re

from rest_framework.exceptions import ValidationError


def validate_youtube_link(value):
    """
    Валидатор для проверки, что ссылка ведет на youtube.com
    """
    # Регулярное выражение для проверки YouTube ссылок
    youtube_pattern = r"^(https?://)?(www\.)?(youtube\.com|youtu\.be)/.+"

    if not re.match(youtube_pattern, value):
        raise ValidationError(
            "Разрешены только ссылки на YouTube (youtube.com или youtu.be)"
        )

    return value


class YouTubeValidator:
    """
    Класс-валидатор для проверки YouTube ссылок
    """

    def __init__(self, field):
        self.field = field

    def __call__(self, value):
        youtube_pattern = r"^(https?://)?(www\.)?(youtube\.com|youtu\.be)/.+"

        # Получаем значение поля
        url = (
            value.get(self.field)
            if isinstance(value, dict)
            else getattr(value, self.field, None)
        )

        if url:
            if not re.match(youtube_pattern, url):
                raise ValidationError(
                    {
                        self.field: "Разрешены только ссылки на YouTube (youtube.com или youtu.be)"
                    }
                )
        return value
