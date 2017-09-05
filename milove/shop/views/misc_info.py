from django.conf.urls import url
from rest_framework.views import APIView
from rest_framework.response import Response

from ..models.misc_info import *
from ..serializers.misc_info import *


class MiscInfoView(APIView):
    def get(self, request, format=None):
        misc_info = MiscInfo.get_solo()
        serializer = MiscInfoSerializer(misc_info)
        return Response(serializer.data)


urlpatterns = [
    url(r'^misc_info/$', MiscInfoView.as_view()),
]
