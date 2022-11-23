from django.core.exceptions import ValidationError
from django.db.models import Sum
from django.db.models.expressions import Exists, OuterRef
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import SAFE_METHODS, IsAuthenticated
from rest_framework.response import Response

from .filters import IngredientFilter, RecipeFilter
from .permissions import IsOwnerOrReadOnly
from .serializers import (
    FavoriteOrShoppingRecipeSerializer,
    FollowSerializer,
    IngredientSerializer,
    RecipesCreateSerializer,
    RecipesListSerializer,
    TagSerializer,
    UserSerializer,
)
from users.models import Follow, User
from recipes.models import (
    AmountIngredient,
    FavoriteRecipe,
    Ingredient,
    Recipe,
    ShoppingCart,
    Tag,
)


class TagsViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientsViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_class = IngredientFilter


class UsersViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @action(
        methods=["GET"], detail=False, permission_classes=(IsAuthenticated,)
    )
    def subscriptions(self, request):
        user = self.request.user
        queryset = Follow.objects.filter(user=user)
        page = self.paginate_queryset(queryset)
        serializer = FollowSerializer(
            page, many=True, context={"request": request}
        )
        return self.get_paginated_response(serializer.data)

    @action(
        methods=["POST", "DELETE"],
        detail=True,
    )
    def subscribe(self, request, id):
        author = get_object_or_404(User, id=id)
        if request.method == "POST":
            if request.user.id == author.id:
                raise ValidationError(
                    "Вы не можете подписаться на свой аккаунт"
                )
            else:
                serializer = FollowSerializer(
                    Follow.objects.create(user=request.user, author=author),
                    context={"request": request},
                )
                return Response(
                    serializer.data, status=status.HTTP_201_CREATED
                )
        elif request.method == "DELETE":
            if Follow.objects.filter(
                user=request.user, author=author
            ).exists():
                Follow.objects.filter(
                    user=request.user, author=author
                ).delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                return Response(
                    {"errors": "Автор отсутсвует в списке подписок"},
                    status=status.HTTP_400_BAD_REQUEST,
                )


class RecipesViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    filter_class = RecipeFilter
    permission_classes = (IsOwnerOrReadOnly,)

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipesListSerializer
        return RecipesCreateSerializer

    def get_queryset(self):
        qs = Recipe.objects.select_related("author").prefetch_related(
            "tags",
            "ingredients",
            "recipe",
            "shopping_cart_recipe",
            "favorite_recipe",
        )
        if self.request.user.is_authenticated:
            qs = qs.annotate(
                is_favorited=Exists(
                    FavoriteRecipe.objects.filter(
                        user=self.request.user, recipe=OuterRef("id")
                    )
                ),
                is_in_shopping_cart=Exists(
                    ShoppingCart.objects.filter(
                        user=self.request.user, recipe=OuterRef("id")
                    )
                ),
            )
        return qs

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        methods=["POST", "DELETE"],
        detail=True,
        permission_classes=(IsAuthenticated,),
    )
    def favorite(self, request, pk):
        recipe_pk = self.kwargs.get("pk")
        recipe = get_object_or_404(Recipe, pk=recipe_pk)
        if request.method == "POST":
            serializer = FavoriteOrShoppingRecipeSerializer(recipe)
            FavoriteRecipe.objects.create(
                user=self.request.user, recipe=recipe
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        elif request.method == "DELETE":
            if FavoriteRecipe.objects.filter(
                user=self.request.user, recipe=recipe
            ).exists():
                FavoriteRecipe.objects.get(
                    user=self.request.user, recipe=recipe
                ).delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                return Response(
                    {"errors": "Рецепт отсутсвует в списке избранных"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

    @action(
        methods=["POST", "DELETE"],
        detail=True,
    )
    def shopping_cart(self, request, pk):
        recipe_pk = self.kwargs.get("pk")
        recipe = get_object_or_404(Recipe, pk=recipe_pk)
        if request.method == "POST":
            serializer = FavoriteOrShoppingRecipeSerializer(recipe)
            ShoppingCart.objects.create(user=self.request.user, recipe=recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        elif request.method == "DELETE":
            if ShoppingCart.objects.filter(
                user=self.request.user, recipe=recipe
            ).exists():
                ShoppingCart.objects.get(
                    user=self.request.user, recipe=recipe
                ).delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                return Response(
                    {"errors": "Рецепт отсутсвует в списке покупок"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

    @action(
        methods=["GET"], detail=False, permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        ingredients = AmountIngredient.objects.select_related(
            "recipe", "ingredient"
        )
        ingredients = ingredients.filter(
            recipe__shopping_cart_recipe__user=request.user
        )
        ingredients = ingredients.values(
            "ingredient__name", "ingredient__measurement_unit"
        )
        ingredients = ingredients.annotate(ingredient_total=Sum("amount"))
        ingredients = ingredients.order_by("ingredient__name")
        shopping_list = "Список покупок: \n"
        for ingredient in ingredients:
            shopping_list += (
                f'{ingredient["ingredient__name"]} - '
                f'{ingredient["ingredient_total"]} '
                f'({ingredient["ingredient__measurement_unit"]}) \n'
            )
            response = HttpResponse(
                shopping_list, content_type="text/plain; charset=utf8"
            )
            response[
                "Content-Disposition"
            ] = 'attachment; filename="shopping_list.txt"'
        return response
