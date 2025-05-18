"""
URL configuration for Drf_Project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django import urls
from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import SimpleRouter
from books.views import BookViewsSet, UserBooksRelationView
from books import views
from debug_toolbar.toolbar import debug_toolbar_urls



rouder = SimpleRouter()

rouder.register(r'books', BookViewsSet)
rouder.register(r'UserBookRelation', UserBooksRelationView)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('social_django.urls', namespace='social')),  # Здесь возможно ошибка если из за этого будет ошибка вместо path писать url
    path('auth/', views.oAuth, name='auth')
] + debug_toolbar_urls()

urlpatterns += rouder.urls