from csv import DictReader

from django.conf import settings
from django.core.management import BaseCommand
from recipes.models import Ingredient


class Command(BaseCommand):
    help = "Loads ingredients from /data"

    def handle(self, *args, **options):
        with open(
            f"{settings.BASE_DIR}/data/ingredients.csv",
            "r",
            encoding="utf-8",
        ) as file:
            reader = DictReader(file)
            Ingredient.objects.bulk_create(
                Ingredient(**data) for data in reader
            )
        self.stdout.write(
            self.style.SUCCESS("***Ingredients were succesfully loaded***")
        )
