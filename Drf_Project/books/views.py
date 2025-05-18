from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from .models import Book
from books.serializers import BooksSerealalizer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from books.permissions import IsOwnerOrReadOnly
from rest_framework.permissions import IsAuthenticated
from books.serializers import BooksUserRelation_serializers
from books.models import UserBookRelation
from rest_framework.mixins import UpdateModelMixin
from rest_framework.viewsets import GenericViewSet
from django.db.models import Count, Case, When, Avg, Value
from django.db.models.functions import Coalesce



from rest_framework.decorators import action


 
class BookViewsSet(ModelViewSet):
    queryset = Book.objects.all().annotate(
            annotated_like = Count(Case(When(userbookrelation__like=True, then = 1))),
            annotated_rating = Coalesce(Avg('userbookrelation__rating'), Value(0.00)))  # Если userbookrelation — это ForeignKey, 
                                                                                                                             # вместо prefetch_related используйте select_related. Для ManyToManyField
                                                                                                                             # или обратных отношений рекомендуется prefetch_related.
    
                                                                                        # Тут сложная строка, обьясняю как она работает:
                                                                                        # Count считает числа которые мы передаём в then тоесть он не совсем
                                                                                        # Считает сколько элементов мы передаём в then то если там два то будет считать что 4 это 2 элемента
                                                                                        # Case и When идут в комлпекте где Case озночает Тогда а Whtn когда
                                                                                        # И потом пишим условия и к нужному обьекту добираемся через(База данных__(Имя обьекта))
                                                                                        
                                                                           
    serializer_class = BooksSerealalizer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    permission_classes = [IsOwnerOrReadOnly]
    filterset_field = ['price']  # Фильтер ищет по одному полю
    search_fields = ['name', 'author_name']   # серч ищет по несколько полям к пример если Hamingway будет и в аторах и в названии нам выведет все совпадения
    ordering_fields = ['price', 'author_name']
    
    
    # В будущем надо будет улучшить эту функцию
    def perform_create(self, serializer):  # Обрабатаваем данные перед сохранением(Этот медот есть в (ModelViewSet) кльлоые у нас прописан в классе но мы тут можем его настраивать)
                                           # Если мы это не сделаем данные просто сохраняться и мы не сможешь добавить свою логику
                                           
        serializer.validated_data['owner'] = self.request.user  # self.request.user возвращает текущего пользователя мы до этого писали permission_classes = [IsAuthenticatedOrReadOnly]
                                                                # Это озночает что пользователь уже должен быть зарегистирован
                                                                 
        serializer.save()
    
    
def oAuth(request):
    return render(request, 'oAuth.html')



class UserBooksRelationView(UpdateModelMixin, GenericViewSet):
    queryset = UserBookRelation.objects.all()
    permission_classes=[IsAuthenticated]
    serializer_class = BooksUserRelation_serializers
    lookup_field = 'book'
    
    def get_object(self):
        obj, _ = UserBookRelation.objects.get_or_create(user = self.request.user, book_id = self.kwargs['book'])  # Здесь мы пишими что либо создаём либо ипзользуем. И взаимзмомот от этого будет с ними дальше работать
        return obj