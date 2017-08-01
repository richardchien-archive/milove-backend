from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import list_route
from rest_framework.routers import SimpleRouter
from rest_framework.permissions import IsAuthenticated

from ..models.coupon import *

router = SimpleRouter()


class CouponViewSet(viewsets.GenericViewSet):
    queryset = Coupon.objects.filter(is_valid=True)
    permission_classes = (IsAuthenticated,)

    @list_route(['GET'])
    def check(self, request):
        result = {
            'discount_amount': 0.0
        }

        try:
            code = request.GET['code']
            price = float(request.GET['price'])
            coupon = self.get_queryset().filter(code=code).first()
            result['discount_amount'] = coupon.calculate_discount_amount(price)
        finally:
            return Response(result)


router.register('coupons', CouponViewSet)

urlpatterns = router.urls
