# Generated by Django 5.0.1 on 2024-02-03 16:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('modelTraining', '0003_remove_traininglabel_image_traininglabel_files'),
    ]

    operations = [
        migrations.CreateModel(
            name='Camera',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('video_source', models.URLField()),
            ],
        ),
    ]
