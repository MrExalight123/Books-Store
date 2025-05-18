from rest_framework.serializers import ModelSerializer

from books.models import Book
from books.models import UserBookRelation
from rest_framework import serializers

class BooksSerealalizer(ModelSerializer):
    likes_count = serializers.SerializerMethodField()
    annotated_like = serializers.IntegerField(read_only = True)
    annotated_rating = serializers.DecimalField(max_digits = 3, decimal_places = 2, required=False, default = 0.00, read_only = True)
    
    class Meta:
        model = Book
        fields = ('id', 'name', 'price', 'author_name', 'owner', 'likes_count', 'annotated_like', 'annotated_rating')  # Здесь можно вместо fields = [Перечислять что надо] можно просто вырезать reader
        
    def get_likes_count(self, instance): # Как тут вообще likes_count находят друг друга и как likes_count определяет что это логика адресована к ней?
                                              # А тут прикол в том что когда мы пишим get_likes_count всё что идёт после get_ будет искать в области видимости функции
                                              # А likes_count мы указали файл что он убираеться на вычисления при подсчёете это поля 
                                              # и поэтому он и обираеться на то что мы написали ниже
            
        return UserBookRelation.objects.filter(book = instance, like = True).count()
    
class BooksUserRelation_serializers(ModelSerializer):
    class Meta:
        model = UserBookRelation
        fields = ('book', 'like', 'in_bookmarks', 'rating')  # Почему мы здесь не стввить id user потомучто пользователь может поставить другое id и его вообще не должно ебать своё id
                                                             # А мы можем получить его id через request --> self.request.user