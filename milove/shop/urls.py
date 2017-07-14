from django.conf.urls import url

from milove.shop import views

urlpatterns = [
    url(r'^products/$', views.products, name='products'),
]
