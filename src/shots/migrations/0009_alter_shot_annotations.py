# Generated by Django 5.1.1 on 2024-09-23 11:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shots', '0008_alter_shot_annotations'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shot',
            name='annotations',
            field=models.ImageField(blank=True, null=True, upload_to='annotations/%Y/%m/%d/'),
        ),
    ]
