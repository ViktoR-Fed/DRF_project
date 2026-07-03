from django.conf import settings
from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, permissions, status, viewsets
from rest_framework.filters import OrderingFilter
from rest_framework.response import Response

from .models import Payment, User
from .serializers import (
    PaymentCreateSerializer,
    PaymentSerializer,
    UserProfileSerializer,
    UserRegistrationSerializer,
    UserSerializer,
    ValidationError,
)
from .services import (
    create_stripe_price,
    create_stripe_product,
    create_stripe_session,
    get_checkout_session,
)


class UserRegistrationView(generics.CreateAPIView):
    """Регистрация нового пользователя"""

    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]


class UserListView(generics.ListAPIView):
    """Список пользователей (только для админов)"""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Просмотр, редактирование, удаление пользователя"""

    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.request.method in ["PUT", "PATCH", "DELETE"]:
            self.permission_classes = [permissions.IsAuthenticated]
        else:
            self.permission_classes = [permissions.AllowAny]
        return super().get_permissions()

    def get_object(self):
        # Пользователь может видеть/редактировать только свой профиль
        return self.request.user


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    permission_classes = [permissions.IsAuthenticated]

    filterset_fields = {
        "paid_course": ["exact"],
        "paid_lesson": ["exact"],
        "payment_method": ["exact"],
    }

    ordering_fields = ["payment_date"]
    ordering = ["-payment_date"]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Payment.objects.all()
        return Payment.objects.filter(user=user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


User = get_user_model()


class UserProfileView(generics.RetrieveAPIView):
    """Получение профиля пользователя с историей платежей"""

    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class PaymentCreateView(generics.CreateAPIView):
    """
    Создание платежа с интеграцией Stripe
    """

    serializer_class = PaymentCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        payment = serializer.save(user=self.request.user)

        # Определяем название продукта
        if payment.paid_course:
            product_name = f"Курс: {payment.paid_course.name}"
            product_description = payment.paid_course.description
        else:
            product_name = f"Урок: {payment.paid_lesson.name}"
            product_description = payment.paid_lesson.description

        try:
            # 1. Создаем продукт в Stripe
            product = create_stripe_product(
                name=product_name, description=product_description
            )
            payment.stripe_product_id = product.id

            # 2. Создаем цену в Stripe
            price = create_stripe_price(
                product_id=product.id, amount=float(payment.amount)
            )
            payment.stripe_price_id = price.id

            # 3. Создаем сессию оплаты
            success_url = f"{settings.YOUR_DOMAIN}/payment/success?session_id={{CHECKOUT_SESSION_ID}}"
            cancel_url = f"{settings.YOUR_DOMAIN}/payment/cancel"

            session = create_stripe_session(
                price_id=price.id,
                success_url=success_url,
                cancel_url=cancel_url,
                payment_id=payment.id,
            )

            payment.stripe_session_id = session.id
            payment.link = session.url

            # Сохраняем изменения
            payment.save()

        except Exception as e:
            # Если что-то пошло не так, удаляем платеж
            payment.delete()
            raise ValidationError(f"Ошибка оплаты: {str(e)}")


class PaymentStatusView(generics.RetrieveAPIView):
    """
    Проверка статуса платежа
    """

    serializer_class = PaymentCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Payment.objects.filter(user=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        payment = self.get_object()

        if payment.stripe_session_id:
            try:
                session = get_checkout_session(payment.stripe_session_id)
                payment.payment_status = session.status
                payment.save()

                return Response(
                    {
                        "payment_id": payment.id,
                        "status": session.status,
                        "customer_email": (
                            session.customer_details.email
                            if session.customer_details
                            else None
                        ),
                        "amount_total": (
                            session.amount_total / 100 if session.amount_total else None
                        ),
                    }
                )
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {
                "payment_id": payment.id,
                "status": payment.payment_status,
            }
        )
