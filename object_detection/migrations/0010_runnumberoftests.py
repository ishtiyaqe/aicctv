# Generated by Django 5.0.1 on 2024-02-21 18:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('object_detection', '0009_alter_downloadedfile_dataset_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='RunNumberOfTests',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('count', models.IntegerField(help_text='100', max_length=255, null=True)),
            ],
        ),
    ]