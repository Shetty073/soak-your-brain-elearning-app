# Generated by Django 3.1 on 2021-01-21 11:51

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('elearn', '0012_assignmentsolution'),
    ]

    operations = [
        migrations.AddField(
            model_name='assignmentsolution',
            name='date',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
