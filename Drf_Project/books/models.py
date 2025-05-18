from site import USER_BASE
from django.db import models
from django.contrib.auth.models import User


class Book(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=7, decimal_places=2)
    author_name = models.CharField(max_length=255)
    owner = models.ForeignKey(User, on_delete = models.SET_NULL, null=True, related_name='my_books')  # Здесь SET_NULL Даёт нам то что если запись будет удаленаа(User) Сама книга останеться
                                                                             # А если бы указали CASCATE То при удаления автора мы бы удалили и книгу
                                                                             
    reader = models.ManyToManyField(User, through='UserBookRelation', related_name='books')  # Здесь мы указаваем что у нас будет доступ к юзерам через UserBookRelation
    
    def __str__(self):
        return f"{self.name} - {self.price:.2f}"
    
    
    
class UserBookRelation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    like = models.BooleanField(default=False)
    in_bookmarks = models.BooleanField(default=False)
    
    OPTION = (
        (1, 'Poop'),
        (2, 'Not bad'),
        (3, 'Normal'),
        (4, 'Good'),
        (5, 'Great'),
    )
    
    rating = models.PositiveBigIntegerField(choices=OPTION, null = True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.book.name}, RATE {self.rating}"
