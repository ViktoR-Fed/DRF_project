from rest_framework import serializers
from .models import Payment, User

class PaymentSerializer(serializers.ModelSerializer):
    user_email = serializers.ReadOnlyField(source='user.email')
    course_name = serializers.ReadOnlyField(source='paid_course.name', allow_null=True)
    lesson_name = serializers.ReadOnlyField(source='paid_lesson.name', allow_null=True)

    class Meta:
        model = Payment
        fields = [
            'id', 'user', 'user_email', 'payment_date',
            'paid_course', 'course_name', 'paid_lesson', 'lesson_name',
            'amount', 'payment_method'
        ]

    def get_course_name(self, obj):
        return obj.paid_course.name if obj.paid_course else None

    def get_lesson_name(self, obj):
        return obj.paid_lesson.name if obj.paid_lesson else None


class UserProfileSerializer(serializers.ModelSerializer):
    """Сериализатор для профиля пользователя с историей платежей"""
    payments = PaymentSerializer(many=True, read_only=True)
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'phone',
            'city',
            'avatar',
            'full_name',
            'payments'
        ]

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip() or obj.email