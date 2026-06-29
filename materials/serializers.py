from rest_framework.serializers import ModelSerializer, SerializerMethodField

from users.models import Subscription
from .validators import validate_youtube_link, YouTubeValidator
from materials.models import Course, Lesson


class LessonSerializer(ModelSerializer):
    class Meta:
        model = Lesson
        fields = "__all__"
        read_only_fields = ["owner"]
        validators = [
            YouTubeValidator(field='video_link')  # Класс-валидатор
        ]

        def validate_video_link(self, value):
            """Функция-валидатор для поля video_link"""
            return validate_youtube_link(value)


class CourseSerializer(ModelSerializer):
    lessons = LessonSerializer(many=True)
    is_subscribed = SerializerMethodField()
    class Meta:
        model = Course
        fields = "__all__"
        read_only_fields = ["owner"]

    def get_is_subscribed(self, obj):
        """Проверяет, подписан ли текущий пользователь на курс"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Subscription.objects.filter(
                user=request.user,
                course=obj
            ).exists()
        return False

class CourseDetailSerializer(ModelSerializer):
    lessons_count = SerializerMethodField()
    lessons = LessonSerializer(many=True, read_only=True)
    is_subscribed = SerializerMethodField()

    class Meta:
        model = Course
        fields = ("name", "description", "preview", "lessons_count", "lessons")
        read_only_fields = ["owner"]

    def get_lessons_count(self, instance):
        return instance.lessons.count()

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Subscription.objects.filter(
                user=request.user,
                course=obj
            ).exists()
        return False