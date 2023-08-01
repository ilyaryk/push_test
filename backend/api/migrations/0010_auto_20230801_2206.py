# Generated by Django 3.2 on 2023-08-01 15:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0009_auto_20230801_2050'),
    ]

    operations = [
        migrations.AddField(
            model_name='ingredient',
            name='recipe',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='ingredients', to='api.recipe'),
        ),
        migrations.AddField(
            model_name='tag',
            name='recipe',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='tags', to='api.recipe'),
        ),
    ]