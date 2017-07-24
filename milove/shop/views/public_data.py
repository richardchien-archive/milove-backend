import django_filters.rest_framework
from django.db.models import Q
from django.utils import timezone
from rest_framework import viewsets
from rest_framework.routers import DefaultRouter
from rest_framework.pagination import PageNumberPagination

from ..models import *
from ..serializers import *
from .. import rest_filters

router = DefaultRouter()


class BrandViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer


router.register('brands', BrandViewSet)


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    class Serializer(serializers.ModelSerializer):
        """Special serializer for CategoryViewSet"""

        class Meta:
            model = models.Category
            exclude = ('super_category',)
            depth = 10  # this is intended to be large

    # the following line is a hack to accomplish self nested serialization
    # https://stackoverflow.com/questions/13376894/django-rest-framework-nested-self-referential-objects

    # noinspection PyProtectedMember
    Serializer._declared_fields['children'] = Serializer(many=True)

    # only get the root level categories,
    # sub categories will be nested in 'children' field
    # see Serializer class
    queryset = Category.objects.filter(super_category=None)
    serializer_class = Serializer


router.register('categories', CategoryViewSet)


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    class Pagination(PageNumberPagination):
        page_size = 20

    class FilterSet(django_filters.rest_framework.FilterSet):
        publish_dt = django_filters.rest_framework.DateFromToRangeFilter()
        sold = django_filters.rest_framework.BooleanFilter()
        brand = rest_filters.CommaSplitListFilter()
        condition = rest_filters.CommaSplitListFilter()
        price = django_filters.rest_framework.RangeFilter()

        class Meta:
            model = Product
            fields = ('publish_dt', 'sold', 'brand', 'condition', 'price')

    def get_queryset(self):
        # only return unsold products and
        # sold products which are sold within 7 days
        return Product.objects.filter(
            Q(sold=False)
            | Q(sold_dt__gt=timezone.now() - timezone.timedelta(days=7))
        )

    serializer_class = ProductSerializer
    pagination_class = Pagination
    filter_class = FilterSet


router.register('products', ProductViewSet, base_name='product')

urlpatterns = router.urls
