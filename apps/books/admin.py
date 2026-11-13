from django.contrib import admin

from .models import Book, Category


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'isbn', 'stock_quantity', 'category')
    search_fields = ('title', 'author', 'isbn')
    list_filter = ('category', 'supplier_country')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    search_fields = ('name',)
