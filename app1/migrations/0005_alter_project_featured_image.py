# Generated by Django 3.2.5 on 2021-07-26 03:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app1', '0004_project_featured_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='featured_image',
            field=models.ImageField(blank=True, default='default.jpg', null=True, upload_to=''),
        ),
    ]
