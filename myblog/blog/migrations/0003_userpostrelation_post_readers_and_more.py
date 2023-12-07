# Generated by Django 4.2.7 on 2023-12-07 10:34

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('blog', '0002_comment'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserPostRelation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('like', models.BooleanField(default=False)),
                ('in_bookmarks', models.BooleanField(default=False)),
                ('post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='blog.post')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='post',
            name='readers',
            field=models.ManyToManyField(related_name='my_actions', through='blog.UserPostRelation', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddConstraint(
            model_name='userpostrelation',
            constraint=models.UniqueConstraint(fields=('user', 'post'), name='unique_relation'),
        ),
    ]
