from django.contrib import admin

from .models import Ingredient, Recipe, Tag, AmountIngredient


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "author",
    )
    list_filter = (
        "name",
        "author",
        "tags",
    )
    empty_value_display = "-пусто-"


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
