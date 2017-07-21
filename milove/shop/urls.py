from django.conf.urls import url
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register('products', views.ProductViewSet)
router.register('categories', views.CategoryViewSet)

urlpatterns = [
    url(r'^get_token/$', views.get_token),
    url(r'^login/$', views.login, name='login'),
    url(r'^get_user_info/$', views.get_user_info),
    url(r'^logout/$', views.logout),
    url(r'^upload/$', views.upload),
    url(r'^checkout/$', views.checkout),
    url(r'^pay-test/$', views.pay_test),
    url(r'^pay-test-paypal/$', views.pay_test_paypal),
]
urlpatterns.extend(router.urls)
