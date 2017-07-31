import django_filters.rest_framework
from rest_framework import viewsets, serializers
from rest_framework.routers import SimpleRouter
from rest_framework.pagination import PageNumberPagination

from ..models.product import *
from ..serializers.product import *
from .. import rest_filters

router = SimpleRouter()


class BrandViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer


router.register('brands', BrandViewSet)


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    class Serializer(serializers.ModelSerializer):
        """Special serializer for CategoryViewSet"""

        class Meta:
            model = Category
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

    class Filter(django_filters.rest_framework.FilterSet):
        published_dt = django_filters.rest_framework.DateFromToRangeFilter()
        sold = django_filters.rest_framework.BooleanFilter()
        brand = rest_filters.CommaSplitListFilter()
        categories = rest_filters.CommaSplitListFilter()
        condition = rest_filters.CommaSplitListFilter()
        original_price = django_filters.rest_framework.RangeFilter()
        price = django_filters.rest_framework.RangeFilter()

        class Meta:
            model = Product
            fields = ('published_dt', 'sold', 'brand', 'categories',
                      'condition', 'original_price', 'price')

    # def get_queryset(self):
    #     # only return unsold products and
    #     # sold products which are sold within 7 days
    #     return Product.objects.filter(
    #         Q(sold=False)
    #         | Q(sold_dt__gt=timezone.now() - timezone.timedelta(days=7))
    #     )

    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    pagination_class = Pagination
    filter_class = Filter
    # most recently published unsold first
    ordering = ('sold', '-published_dt',)
    search_fields = ('brand__name', 'name', 'style', 'size',
                     'categories__name', 'description')


router.register('products', ProductViewSet)

urlpatterns = router.urls
