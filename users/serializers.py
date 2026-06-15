from rest_framework import serializers
from .models import Payment

class PaymentSerializer(serializers.ModelSerializer):
    user_email = serializers.ReadOnlyField(source='user.email')
    course_title = serializers.ReadOnlyField(source='paid_course.name', allow_null=True)
    lesson_title = serializers.ReadOnlyField(source='paid_lesson.name', allow_null=True)

    class Meta:
        model = Payment
        fields = [
            'id', 'user', 'user_email', 'payment_date',
            'paid_course', 'course_name', 'paid_lesson', 'lesson_name',
            'amount', 'payment_method'
        ]