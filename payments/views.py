from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import stripe
import json

from .models import Payment
from .serializers import PaymentSerializer, PaymentCreateSerializer, PaymentStatusSerializer
from orders.models import Order

# Configure Stripe
stripe.api_key = getattr(settings, 'STRIPE_SECRET_KEY', '')


class PaymentCreateView(APIView):
    """Initiate a Stripe payment for an order"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = PaymentCreateSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)

        order_id = serializer.validated_data['order_id']
        order = get_object_or_404(Order, id=order_id, user=request.user)

        # Check if Stripe is configured
        if not stripe.api_key:
            return Response(
                {'error': 'Payment system is not configured. Please contact support.'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

        try:
            # Create Stripe PaymentIntent
            intent = stripe.PaymentIntent.create(
                amount=int(order.total_amount * 100),  # Convert to cents
                currency='usd',
                metadata={
                    'order_id': order.id,
                    'user_email': order.user.email
                }
            )

            # Create Payment record
            payment = Payment.objects.create(
                order=order,
                stripe_payment_intent_id=intent.id,
                amount=order.total_amount,
                status='pending'
            )

            # Update order status
            order.status = 'processing'
            order.save()

            return Response({
                'payment_id': payment.id,
                'client_secret': intent.client_secret,
                'order_id': order.id,
                'amount': str(order.total_amount),
                'status': payment.status
            }, status=status.HTTP_201_CREATED)

        except stripe.error.StripeError as e:
            return Response(
                {'error': f'Payment processing error: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )


class PaymentStatusView(generics.RetrieveAPIView):
    """Get payment status by order ID"""
    serializer_class = PaymentStatusSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        order_id = self.kwargs.get('order_id')
        order = get_object_or_404(Order, id=order_id, user=self.request.user)
        payment = get_object_or_404(Payment, order=order)
        return payment


@method_decorator(csrf_exempt, name='dispatch')
class StripeWebhookView(APIView):
    """Handle Stripe webhook events"""
    permission_classes = []  # Webhook doesn't require authentication

    def post(self, request):
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
        webhook_secret = getattr(settings, 'STRIPE_WEBHOOK_SECRET', '')

        if not webhook_secret:
            # If webhook secret is not configured, just log the event (for testing)
            event = json.loads(payload)
        else:
            try:
                event = stripe.Webhook.construct_event(
                    payload, sig_header, webhook_secret
                )
            except ValueError:
                return Response({'error': 'Invalid payload'}, status=status.HTTP_400_BAD_REQUEST)
            except stripe.error.SignatureVerificationError:
                return Response({'error': 'Invalid signature'}, status=status.HTTP_400_BAD_REQUEST)

        # Handle the event
        if event['type'] == 'payment_intent.succeeded':
            payment_intent = event['data']['object']
            self._handle_payment_succeeded(payment_intent)
        elif event['type'] == 'payment_intent.payment_failed':
            payment_intent = event['data']['object']
            self._handle_payment_failed(payment_intent)

        return Response({'status': 'success'}, status=status.HTTP_200_OK)

    def _handle_payment_succeeded(self, payment_intent):
        """Update payment and order status when payment succeeds"""
        try:
            payment = Payment.objects.get(stripe_payment_intent_id=payment_intent['id'])
            payment.status = 'succeeded'
            payment.save()

            # Update order status
            order = payment.order
            order.status = 'completed'
            order.save()
        except Payment.DoesNotExist:
            pass

    def _handle_payment_failed(self, payment_intent):
        """Update payment status when payment fails"""
        try:
            payment = Payment.objects.get(stripe_payment_intent_id=payment_intent['id'])
            payment.status = 'failed'
            payment.save()

            # Update order status
            order = payment.order
            order.status = 'cancelled'
            order.save()
        except Payment.DoesNotExist:
            pass
