from django.shortcuts import render, redirect, HttpResponse
from .models import User, UserManager, Book
from django.contrib import messages
import bcrypt
import re

# Create your views here.


def index(request):
    return render(request, 'index.html')


def register(request):
    if request.method == "GET":
        return redirect('/')

    errors = User.objects.registration_validator(request.POST)
    if len(errors) > 0:
        for key, value in errors.items():
            messages.error(request, value)
        return redirect('/')
    else:
        password = request.POST['password']
        confirmed_password = request.POST['confirmed_password']

        hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        confirmed_hash = bcrypt.hashpw(
            confirmed_password.encode(), bcrypt.gensalt()).decode()

        new_user = User.objects.create(
            first_name=request.POST['first_name'], last_name=request.POST['last_name'], email=request.POST['email'], password=hashed_pw)
        request.session['user_id'] = new_user.id
        # actually want to redirect to a new success page
        return redirect('/books')


def login(request):
    if request.method == "POST":
        errors = User.objects.login_validator(request.POST)
        if len(errors) > 0:
            for key, value in errors.items():
                messages.error(request, value)
            return redirect('/')

        user = User.objects.filter(email=request.POST['email'])
        if user:
            logged_user = user[0]
            if bcrypt.checkpw(request.POST['password'].encode(), logged_user.password.encode()):
                request.session['user_id'] = logged_user.id
                return redirect('/books')


def books_main(request):
    if request.method == "GET" and 'user_id' not in request.session:
        return redirect('/')
    context = {
        'books': Book.objects.all(),
        'users': User.objects.all(),
        'user': User.objects.get(id=request.session['user_id']),
    }
    return render(request, "main.html", context)


def add_book(request):
    if 'user_id' not in request.session:
        return redirect('/')
    errors = Book.objects.book_validator(request.POST)
    if len(errors) > 0:
        for key, value in errors.items():
            messages.error(request, value)
        return redirect('/books')

    logged_user = User.objects.get(id=request.session['user_id'])
    book_added = Book.objects.create(
        title=request.POST['title'], description=request.POST['description'], uploaded_by=logged_user)
    logged_user.favorited_books.add(book_added)
    return redirect('/books')


def add_to_favorites(request, book_id):
    if 'user_id' not in request.session:
        return redirect('/')
    logged_user = User.objects.get(id=request.session['user_id'])
    book_to_favorite = Book.objects.get(id=book_id)
    logged_user.favorited_books.add(book_to_favorite)
    return redirect('/books')


def book_desc(request, book_id):
    if 'user_id' not in request.session:
        return redirect('/')
    context = {
        'book_described': Book.objects.get(id=book_id),
        'users': User.objects.all(),
        'user': User.objects.get(id=request.session['user_id']),
    }
    return render(request, 'book_desc.html', context)


def edit_book(request, book_id):  # don't forget validations
    if 'user_id' not in request.session:
        return redirect('/')
    logged_user = User.objects.get(id=request.session['user_id'])
    if not logged_user:
        return redirect('/books')

    errors = Book.objects.book_validator(request.POST)
    if len(errors) > 0:
        for key, value in errors.items():
            messages.error(request, value)
        book = Book.objects.get(id=book_id)
        book_id = book.id
        return redirect(f'/books/{book_id}')

    book_to_edit = Book.objects.get(id=book_id)
    book_to_edit.title = request.POST['title']
    book_to_edit.description = request.POST['description']
    book_to_edit.save()
    return redirect('/books')


def delete_book(request, book_id):
    book_to_delete = Book.objects.get(id=book_id)
    book_to_delete.delete()
    return redirect('/books')


def unfavorite(request, book_id):
    logged_user = User.objects.get(id=request.session['user_id'])
    book_to_unfavorite = Book.objects.get(id=book_id)
    logged_user.favorited_books.remove(book_to_unfavorite)
    return redirect('/books')


def logout(request):
    request.session.flush()
    return redirect('/')
