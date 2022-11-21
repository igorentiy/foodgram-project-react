from django.contrib import admin

from .models import AmountIngredient, Ingredient, Recipe, Tag


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ("name", "author", "get_in_favorites")
    list_filter = (
        "name",
        "author",
        "tags",
    )
    empty_value_display = "-пусто-"

    def get_in_favorites(self, obj):
        return obj.favorite_recipe.count()

    get_in_favorites.short_description = "В избранных"


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "measurement_unit",
    )
    list_filter = ("name",)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "color",
    )
    list_filter = ("name",)


@admin.register(AmountIngredient)
class AmountIngredientAdmin(admin.ModelAdmin):
    list_display = ("recipe", "ingredient", "amount")
