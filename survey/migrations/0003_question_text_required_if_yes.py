# Generated by Django 4.2.20 on 2025-04-01 12:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0002_alter_response_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='text_required_if_yes',
            field=models.BooleanField(default=False),
        ),
    ]
