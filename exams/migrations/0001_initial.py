# Generated by Django 5.0.4 on 2024-04-23 18:05

import django.db.models.deletion
import exams.models
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Option',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Exam',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('duration', models.IntegerField(default=60)),
                ('creator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='created_exams', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question_text', models.TextField()),
                ('correct_option', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='correct_for_question', to='exams.option')),
                ('exam', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='questions', to='exams.exam')),
            ],
        ),
        migrations.AddField(
            model_name='option',
            name='question',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='options', to='exams.question'),
        ),
        migrations.CreateModel(
            name='StudentExam',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_time', models.DateTimeField(auto_now_add=True)),
                ('end_time', models.DateTimeField(blank=True, null=True)),
                ('exam', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='exams.exam')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Response',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_correct', models.BooleanField(default=False)),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='exams.question')),
                ('selected_option', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='exams.option')),
                ('student_exam', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='exams.studentexam')),
            ],
        ),
        migrations.AddField(
            model_name='exam',
            name='students',
            field=models.ManyToManyField(related_name='taken_exams', through='exams.StudentExam', to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='CapturedImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stage', models.CharField(choices=[('start', 'Start'), ('mid', 'Middle'), ('end', 'End')], max_length=10)),
                ('image_data', models.ImageField(upload_to=exams.models.captured_image_path)),
                ('is_match', models.BooleanField(default=False)),
                ('student_exam', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='captured_images', to='exams.studentexam')),
            ],
        ),
    ]