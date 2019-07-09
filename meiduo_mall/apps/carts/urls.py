from django.conf.urls import url
from django.contrib import admin
from . import views

urlpatterns = [
    url(r'^carts/$', views.CartsView.as_view()),

    url(r'^carts/undefined/$', views.CartsView.as_view()),

    url(r'^carts/selection/$', views.CartsSelectedAllView.as_view()),
    url(r'^carts/simple/$', views.CartsSimpleView.as_view()),
    url(r'^carts/del/$', views.DeleteSelectedView.as_view()),

]
