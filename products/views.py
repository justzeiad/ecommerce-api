from rest_framework import generics, permissions, filters
from rest_framework.exceptions import PermissionDenied
from django_filters.rest_framework import DjangoFilterBackend
from django.core.cache import cache
from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer, ProductListSerializer


class IsAdminOrReadOnly(permissions.BasePermission):
    """Custom permission: read-only for everyone, write for admin only"""
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff


class CategoryListView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]


class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = 'slug'


class ProductListCreateView(generics.ListCreateAPIView):
    serializer_class = ProductSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'is_active']
    search_fields = ['name', 'description']
    ordering_fields = ['price', 'created_at', 'name']
    ordering = ['-created_at']

    def get_queryset(self):
        cache_key = 'product_list_all'
        queryset = cache.get(cache_key)
        if queryset is not None:
            return queryset

        queryset = Product.objects.select_related('category')
        # Non-admin users only see active products
        if not (self.request.user and self.request.user.is_staff):
            queryset = queryset.filter(is_active=True)
        cache.set(cache_key, queryset, 60 * 5)
        return queryset

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ProductListSerializer
        return ProductSerializer

    def perform_create(self, serializer):
        serializer.save()
        cache.delete('product_list_all')


class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.select_related('category')
    serializer_class = ProductSerializer
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = 'slug'

    def get_queryset(self):
        queryset = super().get_queryset()
        # Non-admin users only see active products
        if not (self.request.user and self.request.user.is_staff):
            queryset = queryset.filter(is_active=True)
        return queryset

    def perform_update(self, serializer):
        serializer.save()
        cache.delete('product_list_all')

    def perform_destroy(self, instance):
        instance.delete()
        cache.delete('product_list_all')
