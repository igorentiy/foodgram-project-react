# Generated by Django 4.1.3 on 2022-11-21 16:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("recipes", "0002_alter_recipe_options_alter_amountingredient_id_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="recipe",
            name="image",
            field=models.ImageField(
                upload_to="recipes/", verbose_name="Фото готового блюда"
            ),
        ),
    ]