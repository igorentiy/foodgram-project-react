from rest_framework import serializers
from recipes.models import Tag
from django.contrib.auth import authenticate
from users.models import User, Follow
from djoser.serializers import CurrentPasswordSerializer, PasswordSerializer
from django.contrib.auth.hashers import make_password
import django.contrib.auth.password_validation as validators


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = (
            "id",
            "name",
            "color",
            "slug",
        )


from rest_framework import serializers


class ObtainTokenSerializer(serializers.Serializer):

    email = serializers.EmailField(max_length=254, required=True)
    password = serializers.CharField(required=True)
    token = serializers.CharField(read_only=True)

    class Meta:
        fields = ("password", "email")

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")
        if email and password:
            user = authenticate(
                request=self.context.get("request"),
                email=email,
                password=password,
            )
            if not user:
                raise serializers.ValidationError(
                    "Проверте электронную почту и пароль"
                )
        else:
            raise serializers.ValidationError(
                "Введите электронную почту и пароль"
            )
        attrs["user"] = user
        return attrs


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
        )

    def get_is_subscribed(self, obj):
        request = self.context.get("request")
        if request is None or request.user.is_anonymous:
            return False
        user = request.user
        return Follow.objects.filter(user=user, author=obj).exists()


class SetUserPasswordSerializer(CurrentPasswordSerializer, PasswordSerializer):
    new_password = serializers.CharField()
    current_password = serializers.CharField()

    def create(self, validated_data):
        user = self.context["request"].user
        password = make_password(validated_data.get("new_password"))
        user.password = password
        user.save()
        return validated_data
