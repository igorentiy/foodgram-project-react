import csv

from django.core.management.base import BaseCommand
from recipe.models import Ingredient


class Command(BaseCommand):
    help = "Loads ingredients from /data"

    def handle(self, *args, **kwargs):
        with open(
                'recipe/data/ingredients.csv', 'r',
                encoding='UTF-8'
        ) as file:
            reader = csv.reader(file, delimiter=",")
            for row in reader:
                Ingredient.objects.get_or_create(
                    name=row[0],
                    measurement_unit=row[1]
                )
        self.stdout.write(
            self.style.SUCCESS("***Ingredients were succesfully loaded***")
        )
