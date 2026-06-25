from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0004_ingredientlinkmapping'),
    ]

    operations = [
        migrations.AddField(
            model_name='ingredientlinkmapping',
            name='ingredient_name_en',
            field=models.CharField(blank=True, default='', max_length=100),
        ),
        migrations.AddField(
            model_name='ingredientlinkmapping',
            name='last_verified_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
