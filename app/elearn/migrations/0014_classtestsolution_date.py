# Generated by Django 3.1 on 2021-01-21 12:03

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('elearn', '0013_assignmentsolution_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='classtestsolution',
            name='date',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
