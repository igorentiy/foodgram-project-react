from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from recipes.models import (
    FavoriteRecipe,
    Ingredient,
    Recipe,
    ShoppingCart,
    Tag,
)
from rest_framework import status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action, api_view
from rest_framework.filters import SearchFilter
from rest_framework.permissions import (
    SAFE_METHODS,
    AllowAny,
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
)
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from users.models import Follow, User

from .filters import RecipeFilter
from .permissions import IsOwnerOrReadOnly
from .serializers import (
    FavoriteOrShoppingRecipeSerializer,
    FollowSerializer,
    IngredientSerializer,
    RecipesCreateSerializer,
    RecipesListSerializer,
    SetUserPasswordSerializer,
    TagSerializer,
    UserSerializer,
)


class TagsViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientsViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (SearchFilter,)
    search_fields = ("^name",)


# class ObtainToken(APIView):
#     serializer_class = ObtainTokenSerializer
#     permission_classes = (AllowAny,)

#     def post(self, request, *args, **kwargs):
#         serializer = ObtainTokenSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         user = serializer.data["user"]
#         token, created = Token.objects.get_or_create(user=user)
#         return Response(
#             {"auth_token": token.key}, status=status.HTTP_201_CREATED
#         )


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
                return Response(
                    {"errors": "Вы не можете подписаться на свой аккаунт"},
                    status=status.HTTP_400_BAD_REQUEST,
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


# @api_view(["post"])
# def set_password(request):
#     serializer = SetUserPasswordSerializer(
#         data=request.data, context={"request": request}
#     )
#     if serializer.is_valid():
#         serializer.save()
#         return Response(
#             {"message": "Пароль успешно изменен"},
#             status=status.HTTP_201_CREATED,
#         )
#     return Response(
#         {"message": "Пароль введён неверно"},
#         status=status.HTTP_400_BAD_REQUEST,
#     )


class RecipesViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    filter_class = RecipeFilter
    permission_classes = (IsOwnerOrReadOnly,)

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipesListSerializer
        return RecipesCreateSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        methods=["POST", "DELETE"],
        detail=True,
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
