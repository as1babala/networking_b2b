# Generated by Django 3.2.13 on 2023-07-19 19:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0015_auto_20230719_1926'),
    ]

    operations = [
        migrations.RenameField(
            model_name='enterprises',
            old_name='company_id',
            new_name='registration_id',
        ),
    ]
