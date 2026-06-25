from django.db import migrations


HEALTH_GOALS = [
    ('fatigue', '피로 개선', 1),
    ('immunity', '면역 관리', 2),
    ('eye_health', '눈 건강', 3),
    ('gut_health', '장 건강', 4),
    ('sleep', '수면 질 개선', 5),
    ('skin_health', '피부 건강', 6),
]

MEDICATION_OPTIONS = [
    ('anticoagulant', '항응고제', 1),
    ('blood_pressure', '혈압약', 2),
    ('diabetes', '당뇨약', 3),
    ('thyroid', '갑상선약', 4),
]

SPECIAL_CONDITION_OPTIONS = [
    ('pregnancy', '임신 또는 수유 중', 1),
    ('liver_disease', '간 질환', 2),
    ('kidney_disease', '신장 질환', 3),
    ('allergy', '알레르기', 4),
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
        ('reports', '0003_reportmessage'),
    ]

    operations = [
        migrations.RunPython(seed_options, remove_seeded_options),
    ]
