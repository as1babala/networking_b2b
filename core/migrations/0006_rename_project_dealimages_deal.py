# Generated by Django 3.2.13 on 2023-12-07 01:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_remove_deals_deal_category'),
    ]

    operations = [
        migrations.RenameField(
            model_name='dealimages',
            old_name='project',
            new_name='deal',
        ),
    ]
