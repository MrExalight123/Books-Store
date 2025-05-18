from django.contrib import admin
from .models import Book
from .models import UserBookRelation 

admin.site.register(Book)
admin.site.register(UserBookRelation)
# Register your models here.
