from django.db import models
from time import gmtime, strftime
from datetime import *
import re
import bcrypt

from django.db.models.fields import CharField, DateTimeField

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
# Create your models here.


class UserManager(models.Manager):
    def registration_validator(self, postData):
        errors = {}
        # email validity
        email = User.objects.filter(email=postData['email'])
        if email:
            errors['unique'] = "Email already in use."
        if not EMAIL_REGEX.match(postData['email']):
            errors['validity'] = "Invalid email address format."
        # first and last name validity
        if len(postData['first_name']) < 2:
            errors['first_name'] = "First name should contain at least 2 characters."
        if len(postData['last_name']) < 2:
            errors['last_name'] = "Last name should contain at least 2 characters."
        if postData['password'] != postData['confirmed_password']:
            errors['password_match'] = "Passwords do not match, try again."
        if len(postData['password']) < 8 and len(postData['confirmed_password']) < 8:
            errors['password_length'] = "Password must be at least 8 characters."
        return errors

    def login_validator(self, postData):
        errors = {}
        user = User.objects.filter(email=postData['email'])
        if user:
            logged_user = user[0]
            if not bcrypt.checkpw(postData['password'].encode(), logged_user.password.encode()):
                errors['invalid'] = "Email or password incorrect."
        if not user:
            errors['account_nonexistent'] = "Account does not exist, please register."
        return errors


class User(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = UserManager()


class BookManager(models.Manager):
    def book_validator(self, postData):
        errors = {}
        existing_book = Book.objects.filter(title=postData['title'])
        if existing_book:
            errors['existing_book'] = "Book has already been uploaded."
        if len(postData['title']) < 1:
            errors['title'] = "Title required for submission."
        if len(postData['description']) < 5:
            errors['description'] = "Description must contain at least 5 characters."
        return errors


class Book(models.Model):
    title = models.CharField(max_length=225)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    uploaded_by = models.ForeignKey(
        User, related_name="books_uploaded", on_delete=models.CASCADE)
    favorited_by = models.ManyToManyField(User, related_name="favorited_books")
    objects = BookManager()
