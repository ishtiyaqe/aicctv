# Generated by Django 5.0.1 on 2024-02-20 21:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('object_detection', '0006_remove_downloadedfile_file_path'),
    ]

    operations = [
        migrations.RenameField(
            model_name='downloadedfile',
            old_name='file_name',
            new_name='dataset',
        ),
        migrations.AddField(
            model_name='downloadedfile',
            name='project',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='downloadedfile',
            name='rf',
            field=models.CharField(max_length=255, null=True),
        ),
    ]
