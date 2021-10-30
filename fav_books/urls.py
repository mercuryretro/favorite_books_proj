from django.urls import path
from . import views

urlpatterns = [
    path('', views.index),
    path('register', views.register),
    path('login', views.login),
    path('logout', views.logout),
    path('books', views.books_main),
    path('books/<int:book_id>', views.book_desc),
    path('add_book', views.add_book),
    path('add_to_favorites/<int:book_id>', views.add_to_favorites),
    path('edit_book/<int:book_id>', views.edit_book),
    path('unfavorite/<int:book_id>', views.unfavorite),
    path('delete_book/<int:book_id>', views.delete_book),
]
