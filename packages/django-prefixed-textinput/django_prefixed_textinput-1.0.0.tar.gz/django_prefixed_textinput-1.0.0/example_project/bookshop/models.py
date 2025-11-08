from django.db import models


class Book(models.Model):
    title = models.CharField("Title", max_length=200)

    author = models.CharField("Author", max_length=200)

    product_code = models.CharField("Product code", max_length=20)

    pages = models.IntegerField("Pages", blank=True)

    isbn_code = models.CharField("ISBN code", max_length=20, blank=True)

    def __str__(self):
        return self.title
