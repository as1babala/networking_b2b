# Generated by Django 3.2.13 on 2023-12-17 02:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_auto_20231210_1645'),
    ]

    operations = [
        migrations.RenameField(
            model_name='subscription',
            old_name='created',
            new_name='created_on',
        ),
        migrations.AlterField(
            model_name='subscription',
            name='status',
            field=models.BooleanField(default=True),
        ),
    ]
