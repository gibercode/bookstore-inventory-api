from rest_framework import mixins, viewsets
from rest_framework.response import Response

from apps.books.models import Book, Category

from .serializers import BookSerializer, CategorySerializer

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


class CategoryViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    pagination_class = None
