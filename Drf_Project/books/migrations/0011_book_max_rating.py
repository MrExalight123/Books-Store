# Generated by Django 5.1.4 on 2024-12-24 11:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0010_alter_userbookrelation_rating'),
    ]

    operations = [
        migrations.AddField(
            model_name='book',
            name='max_rating',
            field=models.DecimalField(decimal_places=2, default=None, max_digits=3),
        ),
    ]
