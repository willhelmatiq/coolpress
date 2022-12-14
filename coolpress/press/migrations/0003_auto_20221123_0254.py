# Generated by Django 3.2.7 on 2022-11-22 23:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('press', '0002_auto_20221114_2127'),
    ]

    operations = [
        migrations.AddField(
            model_name='cooluser',
            name='gh_stars',
            field=models.IntegerField(blank=True, editable=False, null=True),
        ),
        migrations.AddField(
            model_name='cooluser',
            name='gravatar_updated_at',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='cooluser',
            name='last_github_check',
            field=models.DateTimeField(null=True),
        ),
        migrations.AlterField(
            model_name='cooluser',
            name='gh_repositories',
            field=models.IntegerField(blank=True, editable=False, null=True),
        ),
        migrations.AlterField(
            model_name='cooluser',
            name='github_profile',
            field=models.CharField(blank=True, max_length=150, null=True),
        ),
        migrations.AlterField(
            model_name='cooluser',
            name='gravatar_link',
            field=models.URLField(blank=True, editable=False, null=True),
        ),
    ]
