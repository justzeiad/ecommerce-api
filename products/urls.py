from django.urls import path
from .views import (
    CategoryListView,
    CategoryDetailView,
    ProductListCreateView,
    ProductDetailView
)

app_name = 'products'

urlpatterns = [
    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('categories/<slug:slug>/', CategoryDetailView.as_view(), name='category-detail'),
    path('products/', ProductListCreateView.as_view(), name='product-list'),
    path('products/<slug:slug>/', ProductDetailView.as_view(), name='product-detail'),
]
