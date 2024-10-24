# Generated by Django 5.1.1 on 2024-10-17 06:42

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clients', '0005_remove_client_country'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='job',
            name='area',
        ),
        migrations.RemoveField(
            model_name='job',
            name='cost',
        ),
        migrations.AlterField(
            model_name='job',
            name='name',
            field=models.CharField(choices=[('roto', 'Roto'), ('paint', 'Paint'), ('track', 'Track'), ('comp', 'Comp')], max_length=50, unique=True),
        ),
        migrations.CreateModel(
            name='JobRate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cost_per_md', models.DecimalField(decimal_places=2, max_digits=10)),
                ('area', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='job_rates', to='clients.area')),
                ('job', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='job_rates', to='clients.job')),
            ],
            options={
                'unique_together': {('job', 'area')},
            },
        ),
    ]
