from django.contrib import admin

from .forms import BookAdminForm
from .models import Book


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    form = BookAdminForm
    fieldsets = (
        (None, {
            'fields': ('title', 'author', 'product_code',
                       ('pages', 'isbn_code')),
        }),
    )
