from django.shortcuts import get_object_or_404
from rest_framework import serializers
from recipes.models import (
    Tag,
    Recipe,
    FavoriteRecipe,
    ShoppingCart,
    Ingredient,
)
from django.contrib.auth import authenticate
from users.models import User, Follow
from djoser.serializers import CurrentPasswordSerializer, PasswordSerializer
from django.contrib.auth.hashers import make_password
import django.contrib.auth.password_validation as validators
from recipes.models import AmountIngredient
from drf_base64.fields import Base64ImageField
from rest_framework.validators import UniqueTogetherValidator


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = (
            "id",
            "name",
            "color",
            "slug",
        )


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ("id", "name", "measurement_unit")


# class ObtainTokenSerializer(serializers.Serializer):

#     email = serializers.EmailField(max_length=254, required=True)
#     password = serializers.CharField(required=True)
#     token = serializers.CharField(read_only=True)

#     class Meta:
#         fields = ("password", "email")

#     def validate(self, attrs):
#         email = attrs.get("email")
#         password = attrs.get("password")
#         if email and password:
#             user = authenticate(
#                 request=self.context.get("request"),
#                 email=email,
#                 password=password,
#             )
#             if not user:
#                 raise serializers.ValidationError(
#                     "Проверте электронную почту и пароль"
#                 )
#         else:
#             raise serializers.ValidationError(
#                 "Введите электронную почту и пароль"
#             )
#         attrs["user"] = user
#         return attrs


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


class AmountIngredientSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source="ingredient.id")
    name = serializers.ReadOnlyField(source="ingredient.name")
    measurement_unit = serializers.ReadOnlyField(
        source="ingredient.measurement_unit"
    )

    class Meta:
        model = AmountIngredient
        fields = (
            "id",
            "name",
            "measurement_unit",
            "amount",
        )


class AddAmountIngredientSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField()

    class Meta:
        model = AmountIngredient
        fields = (
            "id",
            "amount",
        )


class RecipesListSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    author = UserSerializer(
        read_only=True, default=serializers.CurrentUserDefault()
    )
    ingredients = AmountIngredientSerializer(
        many=True, required=True, source="recipe"
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            "id",
            "tags",
            "author",
            "ingredients",
            "is_favorited",
            "is_in_shopping_cart",
            "name",
            "image",
            "text",
            "cooking_time",
        )

    def get_is_favorited(self, obj):
        request = self.context.get("request")
        if request is None or request.user.is_anonymous:
            return False
        user = request.user
        return FavoriteRecipe.objects.filter(user=user, recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get("request")
        if request is None or request.user.is_anonymous:
            return False
        user = request.user
        return ShoppingCart.objects.filter(user=user, recipe=obj).exists()


class RecipesCreateSerializer(serializers.ModelSerializer):
    ingredients = AddAmountIngredientSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = "__all__"
        read_only_fields = "author"


class FavoriteOrShoppingRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = (
            "id",
            "name",
            "image",
            "cooking_time",
        )


class FollowSerializer(serializers.ModelSerializer):
    email = serializers.ReadOnlyField(source="author.email")
    id = serializers.ReadOnlyField(source="author.id")
    username = serializers.ReadOnlyField(source="author.username")
    first_name = serializers.ReadOnlyField(source="author.first_name")
    last_name = serializers.ReadOnlyField(source="author.last_name")
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
            "recipes",
            "recipes_count",
        )

    def get_is_subscribed(self, obj):
        return Follow.objects.filter(user=obj.user, author=obj.author).exists()

    def get_recipes(self, obj):
        queryset = Recipe.objects.filter(author=obj.author).order_by(
            "-pub_date"
        )
        return FavoriteOrShoppingRecipeSerializer(queryset, many=True).data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj.author).count()
