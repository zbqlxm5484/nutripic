from django.core.management.base import BaseCommand

from reports.iherb_dictionary import load_iherb_ingredients
from reports.models import IngredientLinkMapping


class Command(BaseCommand):
    help = "Import iHerb ingredient URL mappings from ai_data/iherb_category_ingredients.csv."

    def handle(self, *args, **options):
        created = 0
        updated = 0

        for ingredient in load_iherb_ingredients():
            mapping, was_created = IngredientLinkMapping.objects.get_or_create(
                normalized_name=ingredient.canonical_name,
                defaults={
                    "ingredient_name_ko": ingredient.ingredient_name_ko,
                    "ingredient_name_en": "",
                    "iherb_url": ingredient.iherb_url,
                    "iherb_category_name": ingredient.iherb_category_name,
                    "is_active": True,
                },
            )
            if was_created:
                created += 1
            else:
                mapping.ingredient_name_ko = ingredient.ingredient_name_ko
                mapping.ingredient_name_en = mapping.ingredient_name_en or ""
                mapping.iherb_url = ingredient.iherb_url
                mapping.iherb_category_name = ingredient.iherb_category_name
                mapping.save(
                    update_fields=[
                        "ingredient_name_ko",
                        "ingredient_name_en",
                        "iherb_url",
                        "iherb_category_name",
                    ]
                )
                updated += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Imported iHerb mappings: created={created}, updated={updated}"
            )
        )
