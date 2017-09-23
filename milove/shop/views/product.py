import random

import django_filters.rest_framework
import rest_framework.filters
from rest_framework import viewsets, serializers
from rest_framework.decorators import list_route
from rest_framework.response import Response
from rest_framework.routers import SimpleRouter
from rest_framework.pagination import PageNumberPagination
from django.conf import settings
from django.db import models, transaction
from django.db.models import Q

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

    @list_route()
    def hot(self, request, **kwargs):
        try:
            count = int(request.GET['count'])
        except (KeyError, ValueError):
            count = settings.DEFAULT_HOT_CATEGORIES
        queryset = self.get_queryset().filter(
            level=settings.DETAIL_CATEGORY_LEVEL
        ).annotate(
            product_count=models.Count('products')
        ).order_by('-product_count')[:count]
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


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

    class OrderingFilter(rest_framework.filters.OrderingFilter):
        def get_ordering(self, request, queryset, view):
            ordering = super().get_ordering(request, queryset, view)
            if 'sold' not in ordering:
                # make sure sold=False first
                ordering = ('sold',) + tuple(ordering)
            return ordering

    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    pagination_class = Pagination
    filter_class = Filter
    filter_backends = (
        django_filters.rest_framework.DjangoFilterBackend,
        OrderingFilter,  # use custom ordering backend
        rest_framework.filters.SearchFilter
    )

    # most recently published unsold first
    ordering = ('sold', '-published_dt',)
    search_fields = ('brand__name', 'name', 'style', 'size',
                     'categories__name', 'description')

    @list_route()
    def homepage(self, request, **kwargs):
        try:
            count = int(request.GET['count'])
        except (KeyError, ValueError):
            count = settings.DEFAULT_PRODUCTS_ON_HOMEPAGE
        count = min(count, settings.MAX_PRODUCTS_ON_HOMEPAGE)
        queryset = self.get_queryset().filter(
            sold=False).order_by('-show_on_homepage')[:count]
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @list_route()
    def recommendation(self, request, **kwargs):
        try:
            count = int(request.GET['count'])
        except (KeyError, ValueError):
            count = settings.DEFAULT_PRODUCTS_ON_HOMEPAGE
        count = min(count, settings.MAX_RECOMMENDED_PRODUCTS)
        recent = filter(lambda x: x.isdigit(),
                        request.GET.get('recent_visited', '').split(','))
        recent_products = Product.objects.filter(pk__in=recent)[:10]
        brands = set()
        categories = set()
        for prod in recent_products:
            brands.add(prod.brand)
            categories.update(prod.categories.filter(
                level=settings.DETAIL_CATEGORY_LEVEL
            ))

        recommended_products = []
        with transaction.atomic():
            qs = Product.objects.filter(
                Q(brand__in=brands) | Q(categories__in=categories),
                sold=False,
            )
            total_count = qs.count()
            recommended_indexes = random.sample(
                range(total_count),
                k=min(count, total_count)
            )
            [recommended_products.append(qs[i]) for i in recommended_indexes]

        extra_count = count - len(recommended_products)
        if extra_count > 0:
            # not enough
            qs = Product.objects.filter(sold=False).exclude(
                Q(brand__in=brands) | Q(categories__in=categories)
            )
            total_count = qs.count()
            recommended_indexes = random.sample(
                range(total_count),
                k=min(extra_count, total_count)
            )
            [recommended_products.append(qs[i]) for i in recommended_indexes]

        serializer = self.get_serializer(recommended_products, many=True)
        return Response(serializer.data)


router.register('products', ProductViewSet)

urlpatterns = router.urls
