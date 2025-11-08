from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class BookCreateViewTest(TestCase):
    def setUp(self):
        User.objects.create_superuser(username="test", password="test")
        self.client.login(
            username="test",
            password="test",
        )

    def test_book_create_view_loads_successfully(self):
        response = self.client.get(reverse("admin:bookshop_book_add"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "<div class='prefixed-text-input'>")
