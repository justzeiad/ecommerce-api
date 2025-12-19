from django.urls import path
from .views import OrderListView, OrderCreateView, OrderDetailView

app_name = 'orders'

urlpatterns = [
    path('', OrderListView.as_view(), name='order-list'),
    path('create/', OrderCreateView.as_view(), name='order-create'),
    path('<int:order_id>/', OrderDetailView.as_view(), name='order-detail'),
]
