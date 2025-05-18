from django.test import TestCase
from books.serializers import BooksSerealalizer
from books.models import Book
from django.contrib.auth.models import User
from books.models import UserBookRelation
from django.db.models import Count, Case, When, Avg, Value
from django.db.models.functions import Coalesce


class BookSerealalizersTestCase(TestCase):

    def setUp(self):

        self.user1 = User.objects.create(username='Test_User1')
        self.user2 = User.objects.create(username='Test_User2')
        self.user3 = User.objects.create(username='Test_User3')
        self.book1 = Book.objects.create(name='Книга о кабибарах', price=300.00, author_name='кабибара')
        self.book2 = Book.objects.create(name='1000 и один способ', price=1001.00, author_name='Даниил Сергеев')

        UserBookRelation.objects.create(user=self.user1, book=self.book1, like=True)
        UserBookRelation.objects.create(user=self.user2, book=self.book1, like=True)
        UserBookRelation.objects.create(user=self.user3, book=self.book1, like=True)

        UserBookRelation.objects.create(user=self.user1, book=self.book2, like=True)
        UserBookRelation.objects.create(user=self.user2, book=self.book2, like=True)
        UserBookRelation.objects.create(user=self.user3, book=self.book2, like=False)  # Вы спросите, а зачем здесь False, если у нас по умолчанию like=False в модели?
                                                                                       # Потому что если счётчик лайков сломается, он не сможет корректно посчитать количество лайков
                                                                                       # И вместо 2 лайков в book2 придёт 3 — а мы проверяем, что False не учитывается

#       self.book1.reader.set([self.user])  # Возникает вопрос — почему мы не указали reader напрямую у self.book1?
                                           # А всё потому, что нельзя добавлять объект ManyToMany напрямую списком — иначе код выдаст ошибку
        UserBookRelation.objects.create(user=self.user1, book=self.book1, rating=1)
        UserBookRelation.objects.create(user=self.user2, book=self.book1, rating=5)

#      self.book2.reader.set([self.user])


    def test_ok(self):
        books = Book.objects.all().annotate(
            annotated_like=Count(Case(When(userbookrelation__like=True, then=1))))  # Тут достаточно сложная строка, поясняю:
                                                                                    # Count считает количество значений, которые мы передаём в then.
                                                                                    # Case и When идут в паре, где Case означает "в случае", а When — "если"
                                                                                    # И далее мы пишем условия, добираясь до нужного объекта через (таблица__поле)

        books = books.annotate(annotated_rating=Coalesce(Avg('userbookrelation__rating'), Value(0.00)))

        serialalizer1 = BooksSerealalizer(books, many=True).data

        self.client.force_login(self.user1)
        serialalizer2 = [{
            'id': self.book1.id,
            'name': 'Книга о кабибарах',
            'price': '300.00',
            'author_name': 'кабибара',
            'owner': None,
            'likes_count': 3,
            'annotated_like': 3,
            'annotated_rating': '3.00'
        }, {
            'id': self.book2.id,
            'name': '1000 и один способ',
            'price': '1001.00',
            'author_name': 'Даниил Сергеев',
            'owner': None,
            'likes_count': 2,
            'annotated_like': 2,
            'annotated_rating': '0.00'
        }]

        self.assertEqual(serialalizer1, serialalizer2)
