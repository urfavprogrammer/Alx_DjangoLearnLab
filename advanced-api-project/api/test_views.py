from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model

from .models import Author, Book

User = get_user_model()


class BookAPITestCase(APITestCase):
    def setUp(self):
        # Create users
        self.user = User.objects.create_user(username='user1', password='pass')
        self.other_user = User.objects.create_user(username='user2', password='pass')

        # Create authors
        self.author1 = Author.objects.create(name='Author One')
        self.author2 = Author.objects.create(name='Author Two')

        # Create books
        self.book1 = Book.objects.create(title='Django for APIs', publication_year=2020, author=self.author1)
        self.book2 = Book.objects.create(title='Advanced Django', publication_year=2021, author=self.author1)
        self.book3 = Book.objects.create(title='Python Tips', publication_year=2019, author=self.author2)

        self.client = APIClient()

    def test_list_books_unauthenticated(self):
        url = reverse('book-list')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        # Expect at least the three books we created
        titles = [b['title'] for b in resp.data]
        self.assertIn(self.book1.title, titles)
        self.assertIn(self.book2.title, titles)
        self.assertIn(self.book3.title, titles)

    def test_detail_book_unauthenticated(self):
        url = reverse('book-detail', kwargs={'pk': self.book1.pk})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data.get('title'), self.book1.title)

    def test_create_book_requires_auth(self):
        url = reverse('book-create')
        data = {'title': 'New Book', 'publication_year': 2022, 'author': self.author1.pk}
        resp = self.client.post(url, data, format='json')
        # Should be unauthorized for anonymous
        self.assertIn(resp.status_code, (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN))

    def test_create_book_authenticated(self):
        url = reverse('book-create')
        self.client.force_authenticate(user=self.user)
        data = {'title': 'New Book', 'publication_year': 2022, 'author': self.author1.pk}
        resp = self.client.post(url, data, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Book.objects.filter(title='New Book').exists())

    def test_update_book_requires_auth(self):
        url = reverse('book-update', kwargs={'pk': self.book1.pk})
        data = {'title': 'Changed Title'}
        resp = self.client.patch(url, data, format='json')
        self.assertIn(resp.status_code, (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN))

    def test_update_book_authenticated(self):
        url = reverse('book-update', kwargs={'pk': self.book1.pk})
        self.client.force_authenticate(user=self.user)
        data = {'title': 'Changed Title'}
        resp = self.client.patch(url, data, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.book1.refresh_from_db()
        self.assertEqual(self.book1.title, 'Changed Title')

    def test_delete_book_requires_auth(self):
        url = reverse('book-delete', kwargs={'pk': self.book2.pk})
        resp = self.client.delete(url)
        self.assertIn(resp.status_code, (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN))

    def test_delete_book_authenticated(self):
        url = reverse('book-delete', kwargs={'pk': self.book2.pk})
        self.client.force_authenticate(user=self.user)
        resp = self.client.delete(url)
        # Many DRF destroy views return 204 No Content
        self.assertIn(resp.status_code, (status.HTTP_204_NO_CONTENT, status.HTTP_200_OK))
        self.assertFalse(Book.objects.filter(pk=self.book2.pk).exists())

    def test_filter_by_author_and_year_and_title(self):
        url = reverse('book-list')
        # Filter by author1
        resp = self.client.get(url, {'author': self.author1.pk})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        titles = [b['title'] for b in resp.data]
        self.assertIn(self.book1.title, titles)
        self.assertIn(self.book2.title, titles)
        self.assertNotIn(self.book3.title, titles)

        # Filter by year
        resp = self.client.get(url, {'publication_year': 2019})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        titles = [b['title'] for b in resp.data]
        self.assertIn(self.book3.title, titles)
        self.assertNotIn(self.book1.title, titles)

        # Title contains
        resp = self.client.get(url, {'title': 'Django'})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        titles = [b['title'] for b in resp.data]
        self.assertIn(self.book1.title, titles)
        self.assertIn(self.book2.title, titles)

    def test_search_and_ordering(self):
        url = reverse('book-list')
        # Search for "Python" should return book3
        resp = self.client.get(url, {'search': 'Python'})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        titles = [b['title'] for b in resp.data]
        self.assertIn(self.book3.title, titles)

        # Ordering descending by publication_year
        resp = self.client.get(url, {'ordering': '-publication_year'})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        years = [b['publication_year'] for b in resp.data]
        # Ensure list is non-increasing
        self.assertEqual(years, sorted(years, reverse=True))
