from django.conf.urls import url

from milove.shop import views

urlpatterns = [
    url(r'^products/$', views.product_list, name='product-list'),
    url(r'^categories/$', views.category_list, name='category-list'),
]
