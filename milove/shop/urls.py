from django.conf.urls import url
from rest_framework.routers import DefaultRouter

from milove.shop import views

router = DefaultRouter()
router.register('products', views.ProductViewSet)
router.register('categories', views.CategoryViewSet)

# urlpatterns = [
#     url(r'^products/$', views.product_list, name='product-list'),
#     url(r'^categories/$', views.category_list, name='category-list'),
# ]
urlpatterns = router.urls
