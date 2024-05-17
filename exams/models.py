import os
from django.db import models
from django.contrib.auth import get_user_model
from uuid import uuid4

User = get_user_model()


def captured_image_path(instance, filename):
    student_exam = instance.student_exam
    exam_name = student_exam.exam.title
    username = student_exam.student.username
    
    unique_name = f"{uuid4()}{filename}"
    return f"captured_exam_images/{exam_name}/{username}/{unique_name}"


class Exam(models.Model):
    creator = models.ForeignKey(
        User, related_name="created_exams", on_delete=models.CASCADE
    )
    students = models.ManyToManyField(
        User, related_name="taken_exams", through="StudentExam"
    )
    title = models.CharField(max_length=100, unique=True)
    duration = models.IntegerField(default=60)

    def __str__(self):
        return self.title


class StudentExam(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)


class Option(models.Model):
    question = models.ForeignKey(
        "Question", on_delete=models.CASCADE, related_name="options"
    )
    text = models.CharField(max_length=100)

    def __str__(self):
        return self.text


class Question(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name="questions")
    question_text = models.TextField()
    correct_option = models.ForeignKey(
        Option,
        on_delete=models.CASCADE,
        related_name="correct_for_question",
        null=True,
        blank=True,
    )

    def __str__(self):
        return self.question_text


class Response(models.Model):
    student_exam = models.ForeignKey(StudentExam, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_option = models.ForeignKey(Option, on_delete=models.CASCADE)
    is_correct = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        self.is_correct = self.selected_option == self.question.correct_option
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student_exam.student.username}'s response to {self.question}"


class CapturedImage(models.Model):
    student_exam = models.ForeignKey(
        StudentExam, on_delete=models.CASCADE, related_name="captured_images"
    )
    image_data = models.ImageField(upload_to=captured_image_path)
    is_match = models.BooleanField(default=False)
    
