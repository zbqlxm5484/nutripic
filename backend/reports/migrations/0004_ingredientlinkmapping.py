from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0003_reportmessage'),
    ]

    operations = [
        migrations.CreateModel(
            name='IngredientLinkMapping',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('normalized_name', models.CharField(max_length=100, unique=True)),
                ('ingredient_name_ko', models.CharField(max_length=100)),
                ('iherb_url', models.URLField(max_length=500)),
                ('iherb_category_name', models.CharField(blank=True, default='', max_length=200)),
                ('is_active', models.BooleanField(default=True)),
            ],
            options={
                'ordering': ['normalized_name'],
            },
        ),
    ]
