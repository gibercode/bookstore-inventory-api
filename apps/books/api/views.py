from drf_spectacular.utils import extend_schema
from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.books.models import Book, Category

from .serializers import (
    BookSearchParamsSerializer,
    BookSerializer,
    CategorySerializer,
    LowStockParamsSerializer,
)

UUID_REGEX = '[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}'


class BookViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    lookup_value_regex = UUID_REGEX
    queryset = Book.objects.select_related('category').order_by('title', 'id')
    serializer_class = BookSerializer

    def destroy(self, request, *args, **kwargs):
        book = self.get_object()
        data = self.get_serializer(book).data
        book.delete()
        return Response(data)

    @extend_schema(
        parameters=[BookSearchParamsSerializer],
        responses=BookSerializer(many=True),
    )
    @action(detail=False, methods=['get'], url_path='search')
    def search(self, request):
        """List the books of a category (by category id)."""
        params = BookSearchParamsSerializer(data=request.query_params)
        params.is_valid(raise_exception=True)
        queryset = self.get_queryset().filter(category=params.validated_data['category'])
        return self._paginated_response(queryset)

    @extend_schema(
        parameters=[LowStockParamsSerializer],
        responses=BookSerializer(many=True),
    )
    @action(detail=False, methods=['get'], url_path='low-stock')
    def low_stock(self, request):
        """List the books whose stock is at or below the threshold, lowest first."""
        params = LowStockParamsSerializer(data=request.query_params)
        params.is_valid(raise_exception=True)
        queryset = self.get_queryset().filter(
            stock_quantity__lte=params.validated_data['threshold']
        ).order_by('stock_quantity', 'title', 'id')
        return self._paginated_response(queryset)

    def _paginated_response(self, queryset):
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)


class CategoryViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    pagination_class = None
