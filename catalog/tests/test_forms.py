from django.test import TestCase

import datetime

from django.urls import reverse
from django.utils import timezone
from catalog.forms import RenewBookForm
from django.contrib.auth.models import User, Permission
from catalog.models import Author, Book, Genre, BookInstance
from catalog.views import AuthorCreate
import datetime
import uuid


class RenewBookFormTest(TestCase):

    def test_renew_form_date_field_label(self):
        form = RenewBookForm()
        self.assertTrue(form.fields['renewal_date'].label is None or
                        form.fields['renewal_date'].label == 'renewal date')

    def test_renew_form_date_field_help_text(self):
        form = RenewBookForm()
        self.assertEqual(form.fields['renewal_date'].help_text, 'Enter a date between'
                                                                ' now and 4 weeks (default 3).')

    def test_renew_form_date_in_past(self):
        date = datetime.date.today() - datetime.timedelta(days=1)
        form_data = {'renewal_date': date}
        form = RenewBookForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_renew_form_date_too_far_in_future(self):
        date = datetime.date.today() + datetime.timedelta(weeks=4) + datetime.timedelta(days=1)
        form_data = {'renewal_date': date}
        form = RenewBookForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_renew_form_date_today(self):
        date = datetime.date.today()
        form_data = {'renewal_date': date}
        form = RenewBookForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_renew_form_date_max(self):
        date = timezone.now() + datetime.timedelta(weeks=4)
        form_data = {'renewal_data': date}
        form = RenewBookForm(data=form_data)
        self.assertFalse(form.is_valid())


class RenewBookInstanceViewTest(TestCase):
    def setUp(self):
        # Create a user
        test_user1 = User.objects.create_user(username='testuser1',
                                              password='1X<ISRUkw+tuK')
        test_user2 = User.objects.create_user(username='testuser2',
                                              password='2HJ1vRV0Z&3iD')
        test_user1.save()
        test_user2.save()

        # Give test_user2 permission to renew books.
        permission = Permission.objects.get(name='Set book as returned')
        test_user2.user_permissions.add(permission)
        test_user2.save()

        # Create a book
        test_author = Author.objects.create(first_name='John', last_name='Smith')
        test_genre = Genre.objects.create(name='Fantasy')
        test_book = Book.objects.create(
            title='Book Title',
            summary='My book summary',
            isbn='ABCDEFG',
            author=test_author,
        )

        # Create genre as a post_step
        genre_objects_for_book = Genre.objects.all()
        test_book.genre.set(genre_objects_for_book)  # Direct assignment of
        # many-to-many types not allowed
        test_book.save()

        # Create a BookInstance object for test_user1
        return_date = datetime.date.today() + datetime.timedelta(days=5)
        self.test_bookinstance1 = BookInstance.objects.create(
            book=test_book,
            imprint='Unlikely Imprint, 2016',
            due_back=return_date,
            borrower=test_user1,
            status='o',
        )

        # Create a BookInstance object for test_user2
        return_date = datetime.date.today() + datetime.timedelta(days=5)
        self.test_bookinstance2 = BookInstance.objects.create(
            book=test_book,
            imprint='Unlikely Imprint, 2016',
            due_back=return_date,
            borrower=test_user2,
            status='o',
        )

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('renew-book-librarian',
                                           kwargs={'pk': self.test_bookinstance1.pk}))
        # Manually check redirect (Can't use assertRedirect, because the redirect URL is unpredictable)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/accounts/login'))

    def test_forbidden_if_logged_in_but_not_correct_permission(self):
        login = self.client.login(username='testuser1', password='1X<ISRUkw+tuK')
        response = self.client.get(reverse('renew-book-librarian',
                                           kwargs={'pk': self.test_bookinstance1.pk}))
        self.assertEqual(response.status_code, 403)

    def test_logged_in_with_permission_borrowed_book(self):
        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        response = self.client.get(reverse('renew-book-librarian',
                                           kwargs={'pk': self.test_bookinstance2.pk}))

        # Check that it lets us login - this is our book, and we have the right permissions
        self.assertEqual(response.status_code, 200)

    def test_logged_in_with_permission_another_users_borrowed_book(self):
        login = self.client.login(username='testuser2',
                                  password='2HJ1vRV0Z&3iD')
        response = self.client.get(reverse('renew-book-librarian',
                                           kwargs={'pk': self.test_bookinstance1.pk}))

        # Check that it lets us login. We're a librarian, so we can view any users book
        self.assertEqual(response.status_code, 200)

    def test_HTTP404_for_invalid_book_if_logged_in(self):
        # unlikely UID to match our bookinstance!
        test_uid = uuid.uuid4()
        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        response = self.client.get(reverse('renew-book-librarian',
                                           kwargs={'pk': test_uid}))
        self.assertEqual(response.status_code, 404)

    def test_uses_correct_template(self):
        login = self.client.login(username='testuser2',
                                  password='2HJ1vRV0Z&3iD')
        response = self.client.get(reverse('renew-book-librarian',
                                           kwargs={'pk': self.test_bookinstance1.pk}))
        self.assertEqual(response.status_code, 200)

        # Check we used correct template
        self.assertTemplateUsed(response, 'catalog/book_renew_librarian.html')

    def test_form_renewal_date_initially_has_date_three_weeks_in_future(self):
        login = self.client.login(username='testuser2',
                                  password='2HJ1vRV0Z&3iD')
        response = self.client.get(reverse('renew-book-librarian',
                                           kwargs={'pk': self.test_bookinstance1.pk}))
        self.assertEqual(response.status_code, 200)

        date_3_weeks_in_future = datetime.date.today() + datetime.timedelta(weeks=3)
        self.assertEqual(response.context['form'].initial['renewal_date'],
                         date_3_weeks_in_future)

    def test_redirects_to_all_borrowed_books_list_on_success(self):
        login = self.client.login(username='testuser2',
                                  password='2HJ1vRV0Z&3iD')
        valid_data_in_future = datetime.date.today() + datetime.timedelta(weeks=2)
        response = self.client.post(reverse('renew-book-librarian',
                                            kwargs={'pk': self.test_bookinstance1.pk}),
                                    {'renewal_date': valid_data_in_future})
        self.assertRedirects(response, reverse('all-borrowed'))

    def test_form_invalid_renewal_date_past(self):
        login = self.client.login(username='testuser2',
                                  password='2HJ1vRV0Z&3iD')
        date_in_past = datetime.date.today() - datetime.timedelta(weeks=1)
        response = self.client.post(reverse('renew-book-librarian',
                                    kwargs={'pk': self.test_bookinstance1.pk}),
                                    {'renewal_date': date_in_past})

        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'renewal_date',
                             'Invalid date - renewal in past')

    def test_form_invalid_renewal_date_future(self):
        login = self.client.login(username='testuser2',
                                  password='2HJ1vRV0Z&3iD')
        invalid_date_in_future = datetime.date.today() + datetime.timedelta(weeks=5)
        response = self.client.post(reverse('renew-book-librarian',
                                            kwargs={'pk': self.test_bookinstance1.pk}),
                                    {'renewal_date': invalid_date_in_future})
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'renewal_date',
                             'Invalid date - renewal more than 4 weeks ahead')


class AuthorCreateTest(TestCase):

    def test_fields(self):
        form = AuthorCreate()
        self.assertEqual(form.fields, ['first_name', 'last_name', 'date_of_birth', 'date_of_death'])


class AuthorCreateDetailsTest(TestCase):
    def setUp(self):
        # Create a user
        test_user1 = User.objects.create_user(username='testuser1',
                                              password='1X<ISRUkw+tuK')
        test_user2 = User.objects.create_user(username='testuser2',
                                              password='2HJ1vRV0Z&3iD')

        test_user1.save()
        test_user2.save()

        # Give test_user2 permission to create authors.
        perm = Permission.objects.get(name='Can add author')
        test_user2.user_permissions.add(perm)
        test_user2.save()

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('author-create'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/?next=/catalog/author/create/')

    def test_redirect_if_logged_in_but_without_permission(self):
        login = self.client.login(username='testuser1',
                                  password='1X<ISRUkw+tuK')
        response = self.client.get(reverse('author-create'))
        self.assertEqual(response.status_code, 403)

    def test_redirect_if_logged_in_and_permission(self):
        login = self.client.login(username='testuser2',
                                  password='2HJ1vRV0Z&3iD')
        response = self.client.get(reverse('author-create'))
        self.assertEqual(response.status_code, 200)

    def test_uses_correct_template(self):
        login = self.client.login(username='testuser2',
                                  password='2HJ1vRV0Z&3iD')
        response = self.client.get(reverse('author-create'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalog/author_form.html')

    def test_initial_date(self):
        login = self.client.login(username='testuser2',
                                  password='2HJ1vRV0Z&3iD')
        response = self.client.get(reverse('author-create'))
        self.assertEqual(response.status_code, 200)
        initial_date = '11/11/2071'
        self.assertEqual(response.context['form'].initial['date_of_death'],
                         initial_date)

    def test_author_create_by_user_and_redirect_to_author_detail(self):
        login = self.client.login(username='testuser2',
                                  password='2HJ1vRV0Z&3iD')

        Author.objects.create(first_name='Mikel',
                              last_name='Diskein',
                              date_of_birth='2001-10-03')
        new_author_id = Author.objects.get(last_name='Diskein').id
        response = self.client.get(reverse('author-detail',
                                           kwargs={'pk': new_author_id}))
        self.assertEqual(response.status_code, 200)





