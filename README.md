# Books API

REST API для управления книгами и отношением пользователей к ним. Поддерживает социальную авторизацию через GitHub, полностью покрыт юнит тестами

# Функциональность
- CRUD для книг  
- Оценки, лайки и закладки от пользователей  
- Связь пользователя с книгой через модель `UserBookRelation`  
- Аутентификация через GitHub OAuth  
- Поддержка Debug Toolbar для отладки запросов
- тесты покрывающее API serializers

# Стек технологий
- Python + Django  
- Django REST Framework  
- MySQL  
- social-auth-app-django (GitHub OAuth)  
- Django Debug Toolbar

# Установка и запуск

# Подключить бд
Найти в settings

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'mybasedrf',  # имя вашей базы данных
        'USER': 'root',      # имя пользователя
        'PASSWORD': '1234',  # пароль
        'HOST': 'localhost',    # адрес сервера базы данных
        'PORT': '3306',         # порт (по умолчанию 3306)
    }
}

И поставить значеничя своей бд

### Установите зависимости
pip install -r requirements.txt

### Примените миграции
python manage.py migrate

### Запустите сервер
python manage.py runserver

# Струкрута моделей проекта

### Book
- name — название книги

- price — цена книги

- author_name — имя автора

- owner — владелец книги, ForeignKey на модель пользователя (User)

### UserBookRelation
- user — ForeignKey на пользователя (User)

- book — ForeignKey на книгу (Book)

- like — BooleanField, лайк книги

- in_bookmarks — BooleanField, книга в закладках

- rate — IntegerField, оценка книги (от 1 до 5)

