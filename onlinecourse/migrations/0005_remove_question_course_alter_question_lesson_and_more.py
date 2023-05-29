# Generated by Django 4.2.1 on 2023-05-29 05:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('onlinecourse', '0004_remove_submission_grade_question_course_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='question',
            name='course',
        ),
        migrations.AlterField(
            model_name='question',
            name='lesson',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='onlinecourse.lesson'),
        ),
        migrations.AlterField(
            model_name='question',
            name='question_text',
            field=models.CharField(max_length=200),
        ),
        migrations.AddField(
            model_name='question',
            name='course',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='onlinecourse.course'),
        ),
    ]
