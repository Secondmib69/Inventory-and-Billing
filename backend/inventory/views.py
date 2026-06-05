from .models import Product, StockMovement
from .serializers import ProductSeralizer, StockMovementSerializer
from rest_framework import generics
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend
from .filters import ProductFilter, ProductPagePagination, StockMovementPagination
from dj_rest_auth.jwt_auth import JWTCookieAuthentication
from .permissions import IsAdminOrAuthenticatedReadonly
from drf_spectacular.utils import extend_schema, extend_schema_view
from config.openapi import (
    TAG_INVENTORY,
    cursor_param,
    ordering_param,
    page_number_params,
    path_id_param,
    product_filter_params,
    search_param,
)


@extend_schema_view(
    get=extend_schema(
        tags=[TAG_INVENTORY],
        summary='List products',
        description=(
            'Returns a paginated list of products. '
            'Any authenticated user may read; only staff may create (see POST).'
        ),
        parameters=[
            search_param('name', 'sku'),
            *product_filter_params(),
            ordering_param('created_at', 'updated_at', 'price', 'stock', default='-created_at'),
            *page_number_params(),
        ],
    ),
    post=extend_schema(
        tags=[TAG_INVENTORY],
        summary='Create product',
        description=(
            'Create a new product. Staff only. '
            '`sku` and `stock` are read-only on create; use `initial_stock` to seed inventory.'
        ),
        request=ProductSeralizer,
        responses={201: ProductSeralizer},
    ),
)
class ProductListAPIView(generics.ListCreateAPIView):
    authentication_classes = [JWTCookieAuthentication]
    permission_classes = [IsAdminOrAuthenticatedReadonly]
    serializer_class = ProductSeralizer
    queryset = Product.objects.all()
    filter_backends = [SearchFilter, DjangoFilterBackend, OrderingFilter]
    search_fields = ['name', 'sku']
    filterset_class = ProductFilter
    ordering_fields = ['created_at', 'updated_at', 'price', 'stock']
    ordering = ['-created_at']
    pagination_class = ProductPagePagination


@extend_schema_view(
    get=extend_schema(
        tags=[TAG_INVENTORY],
        summary='Retrieve product',
        description='Fetch a single product by ID. Any authenticated user may read.',
        parameters=[path_id_param('product')],
    ),
    put=extend_schema(
        tags=[TAG_INVENTORY],
        summary='Update product',
        description=(
            'Full update of a product. Staff only. '
            '`sku`, `stock`, `created_at`, and `updated_at` cannot be changed directly.'
        ),
        parameters=[path_id_param('product')],
        request=ProductSeralizer,
        responses={200: ProductSeralizer},
    ),
    patch=extend_schema(
        tags=[TAG_INVENTORY],
        summary='Partially update product',
        description='Partial update of a product. Staff only.',
        parameters=[path_id_param('product')],
        request=ProductSeralizer,
        responses={200: ProductSeralizer},
    ),
    delete=extend_schema(
        tags=[TAG_INVENTORY],
        summary='Delete product',
        description='Permanently delete a product. Staff only.',
        parameters=[path_id_param('product')],
        responses={204: None},
    ),
)
class ProductDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes = [JWTCookieAuthentication]
    permission_classes = [IsAdminOrAuthenticatedReadonly]
    serializer_class = ProductSeralizer
    queryset = Product.objects.all()
    lookup_url_kwarg = 'id'


@extend_schema_view(
    get=extend_schema(
        tags=[TAG_INVENTORY],
        summary='List stock movements',
        description=(
            'Returns stock movement history using cursor pagination (newest first). '
            'Admin only.'
        ),
        parameters=[cursor_param()],
    ),
    post=extend_schema(
        tags=[TAG_INVENTORY],
        summary='Record stock movement',
        description=(
            'Record a stock IN or OUT movement and update product stock atomically. '
            'OUT movements fail when available stock is insufficient. Admin only.'
        ),
        request=StockMovementSerializer,
        responses={201: StockMovementSerializer},
    ),
)
class StockMovementsListAPIView(generics.ListCreateAPIView):
    permission_classes = [IsAdminUser]
    authentication_classes = [JWTCookieAuthentication]
    queryset = StockMovement.objects.select_related('product')
    serializer_class = StockMovementSerializer
    pagination_class = StockMovementPagination
