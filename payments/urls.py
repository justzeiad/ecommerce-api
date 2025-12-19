from django.urls import path
from .views import PaymentCreateView, PaymentStatusView, StripeWebhookView

app_name = 'payments'

urlpatterns = [
    path('create/', PaymentCreateView.as_view(), name='payment-create'),
    path('status/<int:order_id>/', PaymentStatusView.as_view(), name='payment-status'),
    path('webhook/', StripeWebhookView.as_view(), name='stripe-webhook'),
]
