from django.db import migrations


HEALTH_GOALS = [
    ('body_fat', '체지방 관리', 7),
    ('bone_health', '뼈 건강', 8),
    ('blood_sugar', '혈당 관리', 9),
]

MEDICATION_OPTIONS = [
    ('cholesterol', '고지혈증약', 5),
    ('stomach', '위장약', 6),
]

SPECIAL_CONDITION_OPTIONS = [
    ('child_teen', '어린이/청소년', 5),
    ('smoking', '흡연', 6),
]


def seed_options(apps, schema_editor):
    HealthGoal = apps.get_model('reports', 'HealthGoal')
    MedicationOption = apps.get_model('reports', 'MedicationOption')
    SpecialConditionOption = apps.get_model('reports', 'SpecialConditionOption')

    upsert_options(HealthGoal, HEALTH_GOALS)
    upsert_options(MedicationOption, MEDICATION_OPTIONS)
    upsert_options(SpecialConditionOption, SPECIAL_CONDITION_OPTIONS)


def upsert_options(model, options):
    for code, name, order in options:
        model.objects.update_or_create(
            code=code,
            defaults={
                'name': name,
                'order': order,
                'is_active': True,
            },
        )


def remove_seeded_options(apps, schema_editor):
    HealthGoal = apps.get_model('reports', 'HealthGoal')
    MedicationOption = apps.get_model('reports', 'MedicationOption')
    SpecialConditionOption = apps.get_model('reports', 'SpecialConditionOption')

    HealthGoal.objects.filter(code__in=[code for code, _, _ in HEALTH_GOALS]).delete()
    MedicationOption.objects.filter(code__in=[code for code, _, _ in MEDICATION_OPTIONS]).delete()
    SpecialConditionOption.objects.filter(code__in=[code for code, _, _ in SPECIAL_CONDITION_OPTIONS]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0006_merge_0004_seed_metadata_options_0005_ingredientlinkmapping_extra_fields'),
    ]

    operations = [
        migrations.RunPython(seed_options, remove_seeded_options),
    ]
