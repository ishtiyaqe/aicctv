# Generated by Django 5.0.1 on 2024-01-26 13:04

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('modelTraining', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='TrainingName',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=224, unique=True)),
            ],
        ),
        migrations.AddField(
            model_name='trainingimages',
            name='name',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='modelTraining.trainingname', to_field='name'),
        ),
        migrations.AddField(
            model_name='traininglabel',
            name='name',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='modelTraining.trainingname', to_field='name'),
        ),
    ]