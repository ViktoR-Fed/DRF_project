from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import ModelSerializer

from .models import Payment, User


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ["email", "password", "password_confirm", "phone", "city", "avatar"]

    def validate(self, data):
        if data["password"] != data["password_confirm"]:
            raise serializers.ValidationError("Пароли не совпадают")
        return data

    def create(self, validated_data):
        validated_data.pop("password_confirm")
        user = User.objects.create_user(**validated_data)
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "phone",
            "city",
            "avatar",
        ]
        read_only_fields = ["id", "email"]


class PaymentSerializer(serializers.ModelSerializer):
    user_email = serializers.ReadOnlyField(source="user.email")
    course_name = serializers.ReadOnlyField(source="paid_course.name", allow_null=True)
    lesson_name = serializers.ReadOnlyField(source="paid_lesson.name", allow_null=True)

    class Meta:
        model = Payment
        fields = [
            "id",
            "user",
            "user_email",
            "payment_date",
            "paid_course",
            "course_name",
            "paid_lesson",
            "lesson_name",
            "amount",
            "payment_method",
            "link",
            "payment_status",
            "stripe_session_id",
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
        fields = ["id", "email", "phone", "city", "avatar", "full_name", "payments"]

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip() or obj.email


class PaymentCreateSerializer(ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            "id",
            "user",
            "paid_course",
            "paid_lesson",
            "amount",
            "payment_method",
            "link",
        ]
        read_only_fields = ["id", "user", "payment_status", "link"]

    def validate(self, data):
        # Проверяем, что указан либо курс, либо урок
        if not data.get("paid_course") and not data.get("paid_lesson"):
            raise ValidationError("Укажите либо курс, либо урок для оплаты")
        return data
