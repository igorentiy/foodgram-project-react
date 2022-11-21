from django.db import models
from users.models import User
from django.core import validators

ORANGE = "#E26C2D"
GREEN = "#49B64E"
PURPLE = "#8775D2"

CHOICES = ((ORANGE, "оранжевый"), (GREEN, "зелёный"), (PURPLE, "фиолетовый"))


class Tag(models.Model):
    name = models.CharField("Тэг", max_length=200, unique=True, blank=False)
    color = models.CharField(
        "Цвет тэга", max_length=7, choices=CHOICES, unique=True, blank=False
    )
    slug = models.SlugField(
        "Slug тэга", max_length=200, unique=True, blank=False
    )

    class Meta:
        verbose_name = "Тэг"
        verbose_name_plural = "Тэги"

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField("Название", max_length=200, blank=False)
    measurement_unit = models.CharField(
        "Единица измерения", max_length=200, blank=False
    )

    class Meta:
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"

    def __str__(self):
        return f"{self.name}, {self.measurement_unit}"


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="recipe",
        verbose_name="Автор",
    )
    name = models.CharField("Название рецепта", max_length=200, blank=False)
    image = models.ImageField(
        "Фото готового блюда", upload_to="static/recipe/", blank=False
    )
    text = models.TextField("Описание приготовления", blank=False, null=True)
    ingredients = models.ManyToManyField(
        Ingredient, through="AmountIngredient"
    )
    tags = models.ManyToManyField(
        Tag, related_name="recipe", verbose_name="Тэги"
    )
    cooking_time = models.PositiveSmallIntegerField(
        "Время приготовления в минутах",
        blank=False,
        validators=(
            validators.MinValueValidator(
                1, message="Время приготовления не может быть меньше 1 минуты"
            ),
        ),
    )
    pub_date = models.DateTimeField(
        "Дата публикации рецепта", auto_now_add=True
    )

    class Meta:
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"
        ordering = ("-pub_date",)

    def __str__(self):
        return self.name


class AmountIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="recipe",
        verbose_name="Рецепт",
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name="ingredient",
        verbose_name="Ингредиент",
    )
    amount = models.PositiveSmallIntegerField("Количество", blank=False)

    class Meta:
        verbose_name = "Количество ингредиента"
        verbose_name_plural = "Количество ингредиентов"
        constraints = [
            models.UniqueConstraint(
                fields=["recipe", "ingredient"],
                name="unique_ingredient",
            )
        ]


class FavoriteRecipe(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="favorite_user",
        verbose_name="Пользователь",
    )

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="favorite_recipe",
        verbose_name="Рецепт",
    )

    class Meta:
        verbose_name = "Количество ингредиента"
        verbose_name_plural = "Количество ингредиентов"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "recipe"],
                name="unique_favorite_recipe",
            )
        ]


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="shopping_cart_user",
        verbose_name="Пользователь",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="shopping_cart_recipe",
        verbose_name="Рецепт",
    )

    class Meta:
        verbose_name = "Список покупок"
        verbose_name_plural = "Списки покупок"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "recipe"],
                name="unique_recipe_in_shopping_cart",
            )
        ]
