import uuid

from django.db import models
from django.db.models import UniqueConstraint, Value
from django.db.models.functions import Replace


class Category(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name_plural = 'categories'
        ordering = ['name']

    def __str__(self):
        return self.name


class Book(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    isbn = models.CharField(max_length=17)
    cost_usd = models.DecimalField(max_digits=10, decimal_places=2)
    selling_price_local = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True
    )
    stock_quantity = models.PositiveIntegerField(default=0)
    category = models.ForeignKey(
        Category, on_delete=models.PROTECT, related_name='books'
    )
    supplier_country = models.CharField(max_length=2, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['title']
        constraints = [
            UniqueConstraint(
                Replace('isbn', Value('-'), Value('')),
                name='unique_book_isbn_digits',
            ),
        ]

    def __str__(self):
        return f'{self.title} ({self.isbn})'
