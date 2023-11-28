from django.test import TestCase
from rango.models import Category
from django.urls import reverse


class CategoryMethodTests(TestCase):
    def test_ensure_views_are_positive(self):
        cat = Category(name='test', views=-1, likes=0)
        cat.save()
        self.assertEqual((cat.views >=0), True)

    def test_slug_line_creation(self):
        cat = Category(name='Test Category')
        cat.save()
        self.assertEqual(cat.slug, 'test-category')


class IndexViewTests(TestCase):
    def test_index_view_with_no_categories(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'There are no categories present.')
        self.assertQuerySetEqual(response.context['categories'], [])