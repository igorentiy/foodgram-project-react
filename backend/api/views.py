from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from rest_framework.decorators import action

# from .serializers import ObtainTokenSerializer
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, SAFE_METHODS
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
    RecipesListSerializer,
    RecipesCreateSerializer,
    FavoriteOrShoppingRecipeSerializer,
    IngredientSerializer,
)
from recipes.models import (
    Tag,
    Recipe,
    FavoriteRecipe,
    ShoppingCart,
    Ingredient,
)
from users.models import User


class TagsViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientsViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


# class ObtainToken(APIView):
#     serializer_class = ObtainTokenSerializer
#     permission_classes = (AllowAny,)

#     def post(self, request, *args, **kwargs):
#         serializer = ObtainTokenSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         user = serializer.validated_data["user"]
#         token, created = Token.objects.get_or_create(user=user)
#         return Response(
#             {"auth_token": token.key}, status=status.HTTP_201_CREATED
#         )


class UsersViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


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
    def favorite(self, request, pk=None):
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
    def shopping_cart(self, request, pk=None):
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
