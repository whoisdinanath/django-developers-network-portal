# Generated by Django 4.0.1 on 2022-01-19 07:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0006_alter_project_featured_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='featured_image',
            field=models.ImageField(blank=True, default='featured_images/default.jpg', null=True, upload_to='featured_images'),
        ),
    ]