from rest_framework.serializers import ModelSerializer, SerializerMethodField

from materials.models import Course, Lesson


class LessonSerializer(ModelSerializer):
    class Meta:
        model = Lesson
        fields = "__all__"
        read_only_fields = ["owner"]


class CourseSerializer(ModelSerializer):
    lessons = LessonSerializer(many=True)

    class Meta:
        model = Course
        fields = "__all__"
        read_only_fields = ["owner"]


class CourseDetailSerializer(ModelSerializer):
    lessons_count = SerializerMethodField()
    lessons = LessonSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = ("name", "description", "preview", "lessons_count", "lessons")
        read_only_fields = ["owner"]

    def get_lessons_count(self, instance):
        return instance.lessons.count()
