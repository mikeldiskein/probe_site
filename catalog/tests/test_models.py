from datetime import date
from django.test import TestCase
from catalog.models import Author, Book, Genre
from catalog.models import BookInstance
import uuid


class AuthorModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        Author.objects.create(first_name='Big', last_name='Bob')

    def test_first_name_label(self):
        author = Author.objects.get(id=1)
        field_label = author._meta.get_field('first_name').verbose_name
        self.assertEquals(field_label, 'first name')

    def test_last_name_label(self):
        author = Author.objects.get(id=1)
        field_label = author._meta.get_field('last_name').verbose_name
        self.assertEquals(field_label, 'last name')

    def test_date_of_birth_label(self):
        author = Author.objects.get(id=1)
        field_label = author._meta.get_field('date_of_birth').verbose_name
        self.assertEquals(field_label, 'date of birth')

    def test_date_of_death_label(self):
        author=Author.objects.get(id=1)
        field_label = author._meta.get_field('date_of_death').verbose_name
        self.assertEquals(field_label, 'died')

    def test_first_name_max_length(self):
        author = Author.objects.get(id=1)
        max_length = author._meta.get_field('first_name').max_length
        self.assertEquals(max_length, 100)

    def test_last_name_max_length(self):
        author = Author.objects.get(id=1)
        max_length = author._meta.get_field('last_name').max_length
        self.assertEquals(max_length, 100)

    def test_objects_name_is_last_name_comma_first_name(self):
        author = Author.objects.get(id=1)
        expected_object_name = f'{author.last_name}, {author.first_name}'
        self.assertEquals(expected_object_name, str(author))

    def test_get_absolute_url(self):
        author = Author.objects.get(id=1)
        self.assertEquals(author.get_absolute_url(), '/catalog/author/1')


class BookModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        Book.objects.create(title='Big Bang')

    def test_title_label(self):
        book = Book.objects.get(id=1)
        field_name = book._meta.get_field('title').verbose_name
        self.assertEquals(field_name, 'title')

    def test_author_label(self):
        book = Book.objects.get(id=1)
        field_name = book._meta.get_field('author').verbose_name
        self.assertEquals(field_name, 'author')

    def test_summary_label(self):
        book = Book.objects.get(id=1)
        field_name = book._meta.get_field('summary').verbose_name
        self.assertEquals(field_name, 'summary')

    def test_isbn_label(self):
        book = Book.objects.get(id=1)
        field_name = book._meta.get_field('isbn').verbose_name
        self.assertEquals(field_name, 'ISBN')

    def test_genre_label(self):
        book = Book.objects.get(id=1)
        field_name = book._meta.get_field('genre').verbose_name
        self.assertEquals(field_name, 'genre')

    def test_max_length_title_label(self):
        book = Book.objects.get(id=1)
        max_length = book._meta.get_field('title').max_length
        self.assertEquals(max_length, 200)

    def test_max_length_summary_label(self):
        book = Book.objects.get(id=1)
        max_length = book._meta.get_field('summary').max_length
        self.assertEquals(max_length, 1000)


    def test_max_length_isbn_label(self):
        book = Book.objects.get(id=1)
        max_length = book._meta.get_field('isbn').max_length
        self.assertEquals(max_length, 13)

    def test_absolute_url_label(self):
        book = Book.objects.get(id=1)
        self.assertEquals(book.get_absolute_url(), '/catalog/book/1')

    def test_str_label(self):
        book = Book.objects.get(id=1)
        expected_name = book.title
        self.assertEquals(expected_name, str(book))


class GenreModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        Genre.objects.create(name='Big Genre')

    def test_name_label(self):
        genre = Genre.objects.get(id=1)
        field_name = genre._meta.get_field('name').verbose_name
        self.assertEquals(field_name, 'name')

    def test_max_length_name_label(self):
        genre = Genre.objects.get(id=1)
        max_length = genre._meta.get_field('name').max_length
        self.assertEquals(max_length, 200)

    def _test_str_label(self):
        genre = Genre.objects.get(id=1)
        expected_name = genre.name
        self.assertEquals(expected_name, str(genre))


class BookInstanceModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        global identity
        identity = uuid.uuid4()
        BookInstance.objects.create(id=identity)

    def test_id_label(self):
        bookinstance = BookInstance.objects.get(id=identity)
        field_name = bookinstance._meta.get_field('id').verbose_name
        self.assertEquals(field_name, 'id')

    def test_book_label(self):
        bookinstance = BookInstance.objects.get(id=identity)
        field_name = bookinstance._meta.get_field('book').verbose_name
        self.assertEquals(field_name, 'book')

    def test_imprint_label(self):
        bookinstance = BookInstance.objects.get(id=identity)
        field_name = bookinstance._meta.get_field('imprint').verbose_name
        self.assertEquals(field_name, 'imprint')

    def test_due_back_label(self):
        bookinstance = BookInstance.objects.get(id=identity)
        field_name = bookinstance._meta.get_field('due_back').verbose_name
        self.assertEquals(field_name, 'due back')

    def test_borrower_label(self):
        bookinstance = BookInstance.objects.get(id=identity)
        field_name = bookinstance._meta.get_field('borrower').verbose_name
        self.assertEquals(field_name, 'borrower')

    def test_max_length_imprint_label(self):
        bookinstance = BookInstance.objects.get(id=identity)
        max_length = bookinstance._meta.get_field('imprint').max_length
        self.assertEquals(max_length, 200)

    def test_status_label(self):
        bookinstance = BookInstance.objects.get(id=identity)
        field_name = bookinstance._meta.get_field('status').verbose_name
        self.assertEquals(field_name, 'status')

    def test_max_length_status(self):
        bookinstance = BookInstance.objects.get(id=identity)
        max_length = bookinstance._meta.get_field('status').max_length
        self.assertEquals(max_length, 1)

    def test_str_label(self):
        bookinstance = BookInstance.objects.get(id=identity)
        expected_name = f'{bookinstance.id} ({bookinstance.book})'
        self.assertEquals(expected_name, str(bookinstance))

    def test_is_overdue_label(self):
        bookinstance = BookInstance.objects.get(id=identity)
        expected_value = bool(bookinstance.due_back and date.today() > bookinstance.due_back)
        self.assertEquals(expected_value, bookinstance.is_overdue)
















