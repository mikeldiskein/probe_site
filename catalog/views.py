import datetime

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin,  PermissionRequiredMixin
from django.contrib.auth.decorators import login_required, permission_required
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from .forms import RenewBookForm
from .models import Book, Author, BookInstance, Genre


def index(request):
    """
    Функция отображения для домашней страницы сайта.
    """
    # Генерация "количеств" некоторых главных объектов
    num_books = Book.objects.all().count()
    # num_books_with_word = Book.objects.filter(author__exact='').count()
    num_instances = BookInstance.objects.all().count()

    # Доступные книги (статус = 'а')
    num_instances_available = BookInstance.objects.filter(status__exact='a').count()
    num_authors = Author.objects.count()  # Метод all применён по умолчанию
    num_genres = Genre.objects.filter(name__icontains='science').count()

    num_visits = request.session.get('num_visits', 1)
    request.session['num_visits'] = num_visits + 1

    context = {
        'num_books': num_books,
        'num_instances': num_instances,
        'num_instances_available': num_instances_available,
        'num_authors': num_authors,
        'num_genres': num_genres,
        'num_visits': num_visits,
    }

    # Отрисовка HTML-шаблона index.html с данными внутри переменной контекста context

    return render(request, 'index.html', context=context)


class BookListView(generic.ListView):
    model = Book
    context_object_name = 'book_list'
    # queryset = Book.objects.filter(title__icontains='мир')
    template_name = 'books/my_template_name_list.html'
    paginate_by = 5


class BookDetailView(generic.DetailView):
    model = Book


class AuthorListView(generic.ListView):
    model = Author
    context_object_name = 'authors'
    template_name = 'authors.html'
    paginate_by = 10


class AuthorDetailView(generic.DetailView):
    model = Author


class LoanedBookByUserListView(LoginRequiredMixin, generic.ListView):
    model = BookInstance
    template_name = 'catalog/bookinstance_list_borrowed_user.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_back')


class Librarian(LoginRequiredMixin, PermissionRequiredMixin, generic.ListView):
    model = BookInstance
    permission_required = 'catalog.can_mark_returned'
    template_name = 'catalog/bookinstance_list_all_borrowed.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(status__exact='o').order_by('due_back')


@login_required
@permission_required('catalog.change_book')
def renew_book_librarian(request, pk):
    book_instance = get_object_or_404(BookInstance, pk=pk)

    if request.method == 'POST':
        form = RenewBookForm(request.POST)

        if form.is_valid():
            book_instance.due_back = form.cleaned_data['renewal_date']
            book_instance.save()

            return HttpResponseRedirect(reverse('all-borrowed'))

    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookForm(initial={'renewal_date': proposed_renewal_date})

    context = {
        'form': form,
        'book_instance': book_instance,
    }

    return render(request, 'catalog/book_renew_librarian.html', context)


class AuthorCreate(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = 'catalog.add_author'
    model = Author
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']
    initial = {'date_of_death': '11/11/2071'}


class AuthorUpdate(UpdateView):
    model = Author
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']


class AuthorDelete(DeleteView):
    model = Author
    success_url = reverse_lazy('authors')


class BookCreate(CreateView):
    model = Book
    fields = '__all__'


class BookUpdate(UpdateView):
    model = Book
    fields = '__all__'


class BookDelete(DeleteView):
    model = Book
    success_url = reverse_lazy('books')





