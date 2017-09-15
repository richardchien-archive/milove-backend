import django_filters.rest_framework
from rest_framework import viewsets, serializers
from rest_framework.response import Response
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


class CategoryTreeSerializer(serializers.ModelSerializer):
    """Special serializer for CategoryViewSet"""

    class Meta:
        model = Category
        exclude = ('super_category',)
        depth = 10  # this is intended to be large


# the following line is a hack to accomplish self nested serialization
# https://stackoverflow.com/questions/13376894/django-rest-framework-nested-self-referential-objects

# noinspection PyProtectedMember
CategoryTreeSerializer._declared_fields['children'] \
    = CategoryTreeSerializer(many=True)


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    class Filter(django_filters.rest_framework.FilterSet):
        level = django_filters.rest_framework.NumberFilter()
        super_category = rest_filters.CommaSplitListFilter()

        class Meta:
            model = Category
            fields = ('level', 'super_category')

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filter_class = Filter

    def list(self, request, *args, **kwargs):
        structure = request.GET.get('structure')
        if structure == 'tree':
            # only get the root level categories,
            # sub categories will be nested in 'children' field
            # see Serializer class
            queryset = self.filter_queryset(self.get_queryset()).filter(
                super_category=None)
            serializer = CategoryTreeSerializer(queryset, many=True)
            return Response(serializer.data)
        # default list structure
        return super().list(request, *args, **kwargs)


router.register('categories', CategoryViewSet)


class AttachmentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Attachment.objects.all()
    serializer_class = AttachmentSerializer


router.register('attachments', AttachmentViewSet)


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    class Pagination(PageNumberPagination):
        page_size = 20
        page_size_query_param = 'page_size'
        max_page_size = 50

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
            fields = ('published_dt', 'show_on_homepage', 'sold',
                      'brand', 'categories', 'condition',
                      'original_price', 'price')

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
