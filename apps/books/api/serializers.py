from decimal import Decimal

from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import IntegrityError, transaction
from rest_framework import serializers

from apps.books.models import Book, Category

from .validators import isbn13_digits

MIN_PRICE = Decimal('0.01')
ISBN_CONSTRAINT = 'unique_book_isbn_digits'


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']


class CategoryField(serializers.PrimaryKeyRelatedField):
    """Write a category by id, read it back as its name."""

    default_error_messages = {
        'does_not_exist': 'Category "{pk_value}" does not exist.',
        'incorrect_type': 'Category id must be a valid UUID.',
    }

    def use_pk_only_optimization(self):
        return False

    def to_internal_value(self, data):
        try:
            return super().to_internal_value(data)
        except DjangoValidationError:
            self.fail('incorrect_type')

    def to_representation(self, value):
        return value.name


class BookSerializer(serializers.ModelSerializer):
    isbn = serializers.CharField(max_length=17)
    category = CategoryField(queryset=Category.objects.all())

    class Meta:
        model = Book
        fields = [
            'id',
            'title',
            'author',
            'isbn',
            'cost_usd',
            'selling_price_local',
            'stock_quantity',
            'category',
            'supplier_country',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {
            'cost_usd': {'min_value': MIN_PRICE},
            'selling_price_local': {'min_value': MIN_PRICE},
        }

    def validate_isbn(self, value):
        isbn13_digits(value)
        return value

    def create(self, validated_data):
        try:
            with transaction.atomic():
                return super().create(validated_data)
        except IntegrityError as exc:
            if ISBN_CONSTRAINT not in str(exc):
                raise
            raise serializers.ValidationError(
                {'isbn': ['A book with this ISBN already exists.']}
            )

    def validate_supplier_country(self, value):
        value = value.upper()
        if len(value) != 2 or not value.isalpha():
            raise serializers.ValidationError('Must be a 2-letter ISO country code.')
        return value
