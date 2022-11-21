from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from .serializers import ObtainTokenSerializer
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from djoser.views import UserViewSet
from rest_framework.decorators import api_view

from .serializers import (
    TagSerializer,
    UserSerializer,
    SetUserPasswordSerializer,
)
from recipes.models import Tag
from users.models import User


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class ObtainToken(APIView):
    serializer_class = ObtainTokenSerializer
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = ObtainTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        token, created = Token.objects.get_or_create(user=user)
        return Response(
            {"auth_token": token.key}, status=status.HTTP_201_CREATED
        )


class UsersViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


@api_view(["post"])
def set_password(request):
    serializer = SetUserPasswordSerializer(
        data=request.data, context={"request": request}
    )
    if serializer.is_valid():
        serializer.save()
        return Response(
            {"message": "Пароль успешно изменен"},
            status=status.HTTP_201_CREATED,
        )
    return Response(
        {"message": "Пароль введён неверно"},
        status=status.HTTP_400_BAD_REQUEST,
    )
