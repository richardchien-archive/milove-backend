from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.exceptions import ParseError, AuthenticationFailed, NotAuthenticated
from rest_framework.response import Response
from django.contrib import auth
from django.middleware import csrf

from .models import *
from .serializers import *


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


@api_view(['GET'])
def get_token(request):
    return Response({'token': csrf.get_token(request)})


@api_view(['POST'])
def login(request):
    if 'username' not in request.data or 'password' not in request.data:
        raise ParseError

    user = auth.authenticate(request, username=request.data['username'], password=request.data['password'])
    if not user:
        raise AuthenticationFailed

    auth.login(request, user)

    serializer = UserInfoSerializer(user.userinfo)
    return Response(serializer.data)


@api_view(['POST'])
def logout(request):
    auth.logout(request)
    return Response()
