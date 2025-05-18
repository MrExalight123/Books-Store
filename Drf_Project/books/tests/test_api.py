
from rest_framework.test import APITestCase
from django.urls import reverse
from books.models import Book
from books.serializers import BooksSerealalizer
from rest_framework import status
import json
from django.contrib.auth.models import User
from books.models import UserBookRelation
from django.db.models import Count, Case, When
from django.db.models import Count, Case, When, Avg, Value
from django.db.models.functions import Coalesce



class BooksApiTestCase(APITestCase):
    
    def setUp(self):
        self.user = User.objects.create(username = 'test_username')
        self.book1 = Book.objects.create(name = 'Укус питона', price = 1400.00, author_name = 'Андрей Великий', owner = self.user)
        self.book2 = Book.objects.create(name = 'Искуство войны Андрей Великий', price = 2100.00, author_name = 'Цзинь Цзунь',)
        self.book3 = Book.objects.create(name = 'Как сделать кресло', price = 2000.00, author_name = 'Трансформер')
        
    def test_get(self):
        url = reverse('book-list')
        respoce = self.client.get(url)
        books = Book.objects.all().annotate(
            annotated_like = Count(Case(When(userbookrelation__like=True, then = 1))),
            annotated_rating = Coalesce(Avg('userbookrelation__rating'), Value(0.00)))
        serializer_data = BooksSerealalizer(books, many=True).data
        self.assertEqual(status.HTTP_200_OK, respoce.status_code)
        self.assertEqual(respoce.data, serializer_data)
        
    def test_get_filter(self):
        serializer_data = Book.objects.filter(id__in=[self.book1.id, self.book2.id]).annotate(
            annotated_like = Count(Case(When(userbookrelation__like = True, then= 1))),
            annotated_rating = Coalesce(Avg('userbookrelation__rating'), Value(0.00)))
        
        url = reverse('book-list')  # Почему мы не пишим сюда data={'search' : 2100.00} потомучто reverse принимает только один аргумент
        respoce = self.client.get(url, data={'search' : 'Андрей Великий'})
        serializer_data = BooksSerealalizer(serializer_data, many=True).data
        self.assertEqual(status.HTTP_200_OK, respoce.status_code)
        self.assertEqual(respoce.data, serializer_data)
        
    def test_get_ordering(self):
        url = reverse('book-list')
        books = Book.objects.filter(id__in = [self.book1.id, self.book3.id, self.book2.id]).annotate(
            annotated_like = Count(Case(When(userbookrelation__like = True, then = 1)))
        ).order_by(
            Case(
                When(id = self.book1.id, then = 0), 
                When(id = self.book3.id, then = 1), 
                When(id = self.book2.id, then = 2),
            )
        )
        books = books.annotate(
            annotated_rating = Coalesce(Avg('userbookrelation__rating'), Value(0.00))
        )
        
        respoce = self.client.get(url, data = {'ordering' : 'price'})
        serializer_data = BooksSerealalizer(books, many=True).data
        self.assertEqual(status.HTTP_200_OK, respoce.status_code)
        self.assertEqual(respoce.data, serializer_data)
        
    def test_get_ordering_reverse(self):
        url = reverse('book-list')
        books = Book.objects.all().annotate(
            annotated_like = Count(Case(When(userbookrelation__like = True, then = 1)))
        ).order_by(
            Case(
                When(id = self.book2.id, then = 0),
                When(id = self.book3.id, then = 1),
                When(id = self.book1.id, then = 2),
            )
        )
        
        books = books.annotate(
            annotated_rating = Coalesce(Avg('userbookrelation__rating'), Value(0.00))
        )
        respoce = self.client.get(url, data = {'ordering' : '-price'})
        serializer_data = BooksSerealalizer(books, many=True).data
        self.assertEqual(status.HTTP_200_OK, respoce.status_code)
        self.assertEqual(respoce.data, serializer_data)
        
    def test_create(self):
        url = reverse('book-list')
        data = {"price" : 15100,
                "name" : "412",
                "author_name" : "5125",}
        self.client.force_login(self.user)
        json_data = json.dumps(data)
        respoce = self.client.post(url, data = json_data, content_type='application/json')
        book_list = self.client.get(url).data
        data_get = [{
                     'id': 1,
                     'name': 'Укус питона',
                     'price': '1400.00',
                     'author_name': 'Андрей Великий',
                     'owner': self.user,
                     'likes_count' : 0,
                     'annotated_rating' : 0,},
                    {'id': 2, 
                     'name': 'Искуство войны Андрей Великий',
                     'price': '2100.00',
                     'author_name': 'Цзинь Цзунь',
                     'owner': None,
                     'likes_count' : 0,
                     'annotated_rating' : 0,},
                    {'id': 3,
                     'name': 'Как сделать кресло', 
                     'price': '2000.00', 
                     'author_name': 'Трансформер',
                     'owner': None,
                     'likes_count' : 0,
                     'annotated_rating' : 0,},
                    {'id': 4,
                     'name': '412', 
                     'price': '15100.00',
                     'author_name': '5125',
                     'owner' : self.user,
                     'likes_count' : 0,
                     'annotated_rating' : 0,}]
        self.assertEqual(status.HTTP_201_CREATED, respoce.status_code)
#        self.assertEqual(book_list, data_get)  # Надо будет это исправить
        self.assertEqual(4, Book.objects.all().count())  # Проверяем сколько книг стало после прибавления(Так мы проверяем и удаления и добавления)
        
    def test_put(self):
        url = reverse('book-detail', args=(self.book1.id,))
        data = {'id' : 1,
                "price" : '151.00',
                "name" : "Укус питона",
                "author_name" : "Андрей Великий",}
        self.client.force_login(self.user)
        json_data = json.dumps(data)
        respoce = self.client.put(url, data = json_data, content_type='application/json')
        self.assertEqual(status.HTTP_200_OK, respoce.status_code)
        self.book1.refresh_from_db()  # Надо рефрешать перед этим чтобы вывелось коретный book1 после того как мы сделали PUT
        self.assertEqual(151.00, self.book1.price)
        
    def test_delete(self):
        url = reverse('book-detail', args=(self.book1.id,))
        url2 = reverse('book-list')
        self.client.force_login(self.user)
        respoce = self.client.delete(url, content_type='application/json')
        book_list = self.client.get(url2).data
        self.assertEqual(status.HTTP_204_NO_CONTENT, respoce.status_code)
        data = [{'id': self.book2.id,
                 'name': 'Искуство войны Андрей Великий',
                 'price': '2100.00', 'author_name': 'Цзинь Цзунь',
                 'owner' : None,
                 'likes_count' : 0,
                 'annotated_like': 0,
                 'annotated_rating': '0.00',},
                {'id': self.book3.id,
                 'name': 'Как сделать кресло', 
                 'price': '2000.00',
                 'author_name': 'Трансформер',
                 'owner' : None,
                 'likes_count' : 0,
                 'annotated_like': 0,
                 'annotated_rating': '0.00',}]
        self.assertEqual(book_list, data)
        
    def test_put_no_owner(self):
        self.user2 = User.objects.create(username = 'test_username2')
        url = reverse('book-detail', args=(self.book1.id,))
        data = {'id' : 1,
                "price" : '151.00',
                "name" : "Укус питона",
                "author_name" : "Андрей Великий",
                'owner': 3,
                'likes_count': 0,
                'annotated_rating': '0.00',}
        self.client.force_login(self.user2)
        json_data = json.dumps(data)
        respoce = self.client.put(url, data = json_data, content_type='application/json')
        self.assertEqual(status.HTTP_403_FORBIDDEN, respoce.status_code)
        self.book1.refresh_from_db()
        self.assertEqual(1400.00, self.book1.price)
        
    def test_delete_no_owner(self):
        self.user2 = User.objects.create(username = 'test_username2')
        url = reverse('book-detail', args=(self.book1.id,))
        url2 = reverse('book-detail', args=(self.book1.id,))
        self.client.force_login(self.user2)
        respoce = self.client.delete(url, content_type='application/json')
        book_list = self.client.get(url2).data
        self.book1.refresh_from_db()
        data_delete = {
                     'id': self.book1.id,
                     'name': 'Укус питона',
                     'price': '1400.00',
                     'author_name': 'Андрей Великий',
                     'owner': self.book1.owner.id,
                     'likes_count' : 0,
                     'annotated_like': 0,
                     'annotated_rating': '0.00',}
        self.book1.refresh_from_db()
        self.assertEqual(book_list, data_delete)
        self.assertEqual(status.HTTP_403_FORBIDDEN, respoce.status_code)
        
class UserBookRelationTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create(username = 'test_username')
        self.book1 = Book.objects.create(name = 'Укус питона', price = 1400.00, author_name = 'Андрей Великий', owner = self.user)
        self.book2 = Book.objects.create(name = 'Искуство войны Андрей Великий', price = 2100.00, author_name = 'Цзинь Цзунь',)
        
        self.book1Relation = UserBookRelation.objects.create(user = self.user, book = self.book1)
        
    def test_like(self):
        self.client.force_login(self.user)
        url = reverse('userbookrelation-detail', args=(self.book1.id,))
        data_like = {
            'like' : True
        }
        json_data = json.dumps(data_like)
        respoce = self.client.patch(url, data = json_data, content_type ='application/json')
        self.assertEqual(status.HTTP_200_OK, respoce.status_code)
        self.book1Relation.refresh_from_db()
        self.assertTrue(self.book1Relation.like)
        
    def test_bookmarks(self):
        self.client.force_login(self.user)
        url = reverse('userbookrelation-detail', args=(self.book1.id,))  # Эту запятую обязательно ставить
        data_bookmarks = {
            'in_bookmarks' : True
        }
        json_data = json.dumps(data_bookmarks)
        respoce = self.client.patch(url, data = json_data, content_type= 'application/json')
        self.assertEqual(status.HTTP_200_OK, respoce.status_code)
        self.book1Relation.refresh_from_db()
        self.assertTrue(self.book1Relation.in_bookmarks)
        
    def test_rating(self):
        self.client.force_login(self.user)
        url = reverse('userbookrelation-detail', args=(self.book1.id,))  # Эту запятую обязательно ставить
        data_bookmarks = {
            'rating' : 3
        }
        json_data = json.dumps(data_bookmarks)
        respoce = self.client.patch(url, data = json_data, content_type= 'application/json')
        self.assertEqual(status.HTTP_200_OK, respoce.status_code)
        self.book1Relation.refresh_from_db()
        self.assertEqual(3, self.book1Relation.rating)
        
    # Тут мы проверяем что будет если передать 6 а не число от 1 до 5(Рейтинг на который мы расчитаваем) он должен выдать ошибку     
    def test_rating_error(self):
        self.client.force_login(self.user)
        url = reverse('userbookrelation-detail', args=(self.book1.id,))  # Эту запятую обязательно ставить
        data_bookmarks = {
            'rating' : 6
        }
        json_data = json.dumps(data_bookmarks)
        respoce = self.client.patch(url, data = json_data, content_type= 'application/json')
        self.assertEqual(status.HTTP_400_BAD_REQUEST, respoce.status_code)