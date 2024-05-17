import random
from django.contrib import messages
from django.forms import model_to_dict
from django.views.decorators.csrf import csrf_exempt
from django.http import (
    HttpResponse,
    HttpResponseBadRequest,
    HttpResponseRedirect,
    JsonResponse,
)
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from exams.tasks import face_rec_task
from .models import (
    Exam,
    StudentExam,
    CapturedImage,
    Question,
    Response as QResponse,
    Option,
)
from users.models import Image
from users.face import encode_and_compare_faces, face_check
from django.shortcuts import render
from .models import Exam
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from PIL import Image as PilImage
import numpy as np
from io import BytesIO

User = get_user_model()


def index(request):
    return HttpResponse("Exam App")


@login_required()
def list_exams(request):
    exams = Exam.objects.all()
    return render(request, "list_exams.html", {"exams": exams})


@login_required()
def view_exam(request, exam_id):
    exam = get_object_or_404(Exam, pk=exam_id)
    return render(request, "view_exam.html", {"exam": exam})


@login_required()
def start_exam(request, exam_id):
    exam = get_object_or_404(Exam, pk=exam_id)
    user = request.user
    if request.method == "GET":
        return render(request, "start_exam.html", {"exam": exam})
    input_face = request.FILES.get("image", None)
    if not input_face:
        messages.error(request, "Please provide face info by capturing image")
        return HttpResponseBadRequest("Please provide face info by capturing an image")
    if input_face:
        # Trying to convert the image to np_array
        img = PilImage.open(input_face)
        img_np = np.array(img)

        user_images = Image.objects.filter(user=user)
        user_images_np = [np.array(PilImage.open(image.image)) for image in user_images]

        face_match = encode_and_compare_faces(
            input_face=img_np, user_faces=user_images_np
        )

        if not face_match:
            student_exam = StudentExam.objects.create(
                student=user, exam=exam, start_time=timezone.now
            )
            captured_image = CapturedImage.objects.create(
                student_exam=student_exam,
                image_data=input_face,
                stage="start",
                is_match=False,
            )

            captured_image.save()

            return redirect(reverse("exams:exam_question", kwargs={"exam_id": exam_id}))

        if face_match:
            student_exam = StudentExam.objects.create(
                student=user, exam=exam, start_time=timezone.now
            )
            captured_image = CapturedImage.objects.create(
                student_exam=student_exam,
                image_data=input_face,
                stage="start",
                is_match=True,
            )

            captured_image.save()

            return redirect(reverse("exams:exam_question", kwargs={"exam_id": exam_id}))

    else:
        messages.error(request, "Photo not provided.")
        return render(request, "start_exam.html", {"exam": exam})



@login_required
def exam_question(request, exam_id):
    exam = get_object_or_404(Exam, pk=exam_id)
    total_questions = exam.questions.count()

    if request.method == "GET":
        student_exam = StudentExam.objects.filter(student=request.user, exam=exam).first()
        answered_questions_count = QResponse.objects.filter(student_exam=student_exam).count()

        if answered_questions_count == total_questions:
            return HttpResponseRedirect(reverse("exams:end_exam_result", kwargs={"exam_id": exam_id}))

        answered_question_ids = QResponse.objects.filter(student_exam=student_exam).values_list("question__id", flat=True)
        remaining_questions = exam.questions.exclude(id__in=answered_question_ids)

        if not remaining_questions:
            return HttpResponse("You have answered all questions.")

        random_question = random.choice(remaining_questions)
        return render(request, "exam_question.html", {"exam": exam, "question": random_question})

    elif request.method == "POST":
        user = request.user
        question_id = request.POST.get("question_id")
        selected_option_id = request.POST.get("answer")

        if not question_id or not selected_option_id:
            return HttpResponseRedirect(reverse("exams:exam_question", kwargs={"exam_id": exam_id}))

        question = get_object_or_404(Question, pk=question_id)
        selected_option = get_object_or_404(Option, pk=selected_option_id)
        
        student_exam, created = StudentExam.objects.get_or_create(student=user, exam=exam)

        if QResponse.objects.filter(student_exam=student_exam, question=question).exists():
            return HttpResponse("You have already answered this question.")

        response = QResponse.objects.create(
            student_exam=student_exam,
            question=question,
            selected_option=selected_option,
        )

        return HttpResponseRedirect(reverse("exams:exam_question", kwargs={"exam_id": exam_id})
        )



@login_required()
def end_exam_verification(request, exam_id):
    exam = get_object_or_404(Exam, pk=exam_id)
    user = request.user

    if request.method == "GET":
        return render(request, "end_exam_verification.html", {"exam": exam})

    input_face = request.FILES.get("image", None)

    if not input_face:
        messages.error(
            request, "Please provide face information by capturing an image."
        )
        return HttpResponseBadRequest(
            "Please provide face information by capturing an image."
        )

    img = PilImage.open(input_face)
    img_np = np.array(img)

    user_images = Image.objects.filter(user=user)
    user_images_np = [np.array(PilImage.open(image.image)) for image in user_images]

    student_exam = get_object_or_404(StudentExam, student=user, exam=exam)
    face_match = encode_and_compare_faces(input_face=img_np, user_faces=user_images_np)

    captured_image = CapturedImage.objects.create(
        student_exam=student_exam,
        image_data=input_face,
        stage="end",
        is_match=face_match,
    )
    captured_image.save()

    return HttpResponseRedirect(
        reverse("exams:end_exam_result", kwargs={"exam_id": exam_id})
    )


@csrf_exempt
@login_required
def end_exam_result(request, exam_id):
    exam = get_object_or_404(Exam, pk=exam_id)
    return render(request, "end_exam_result.html", {"exam": exam})


@csrf_exempt
@login_required
def start_exam_api(request, exam_id):
    if request.method == "POST":
        user = request.user
        exam = Exam.objects.filter(pk=exam_id).first()

        if not exam:
            return JsonResponse(
                {
                    "success": False,
                    "message": "Exam not found",
                    "status": 404,
                }
            )

        if StudentExam.objects.filter(student=user, exam=exam).exists():
            return JsonResponse(
                {
                    "success": False,
                    "message": f"You have taken this Exam Already",
                    "data": None,
                    "status": 409,
                }
            )

        StudentExam.objects.create(student=user, exam=exam, start_time=timezone.now)

        questions_data = []
        for question in exam.questions.all():
            question_data = {
                "question_id": question.id,
                "question_text": question.text,
                "options": [option.text for option in question.options.all()],
            }
            questions_data.append(question_data)

        return JsonResponse(
            {
                "success": True,
                "message": f"You've started {exam.title} Exam successfully",
                "data": {"exam": model_to_dict(exam), "questions": questions_data},
            }
        )

    elif request.method == "GET":
        exam = Exam.objects.filter(pk=exam_id).first()
        if not exam:
            return JsonResponse(
                {
                    "success": False,
                    "message": "Exam not found",
                    "status": 404,
                }
            )
        return render(request, "exam.html", {"exam": model_to_dict(exam)})

    else:
        return JsonResponse({"error": "Method not allowed"}, status=405)


@csrf_exempt
@login_required
def exam_verification_api(request, exam_id):
    if request.method == "POST":
        print("verification_url=======")
        exam = get_object_or_404(Exam, pk=exam_id)
        user = request.user
        image = request.FILES.get("live_pic")
        
        student_exam, created = StudentExam.objects.get_or_create(student=user, exam=exam)

        captured_image = CapturedImage.objects.create(
            student_exam=student_exam, image_data=image
         )
        
        print('infos',exam_id, user.id, captured_image.id)
        
        face_rec_task.delay(exam_id, user.id, captured_image.id)
        
        
        
        
        return JsonResponse(
                {
                    "task_info": "sent",
                    "success": True,
                    "code": 201,
                    "message": "face recieved successfully",
                }
            )
        
        # print("live_pic", image)
        # incoming_np_array = np.asarray(PilImage.open(image))

        # face_in_image = face_check(incoming_np_array)
        # print("face_in_image", face_in_image)
        # if not face_in_image:
        #     return JsonResponse(
        #         {
        #             "success": False,
        #             "code": 446,
        #             "message": "No face detected in the image.",
        #             "data": {"face_detected": False},
        #         }
        #     )

        # user_images = Image.objects.filter(user=user)
        # user_images_np = [np.array(PilImage.open(image.image)) for image in user_images]

        # # print("user_images_np", user_images_np)

        # student_exam, created = StudentExam.objects.get_or_create(
        #     student=user, exam=exam
        # )
        # print("student_exam", student_exam)
        # face_match = encode_and_compare_faces(
        #     input_face=incoming_np_array, user_faces=user_images_np
        # )

        # CapturedImage.objects.create(
        #     student_exam=student_exam, image_data=image, is_match=face_match
        # )

        # if face_match:
        #     return JsonResponse(
        #         {
        #             "success": True,
        #             "code": 456,
        #             "message": "face verification is successful",
        #         }
        #     )
        # if not face_match:
            # return JsonResponse(
            #     {
            #         "success": False,
            #         "code": 466,
            #         "message": "face verification failed, but you can continue with your exam",
            #     }
            # )
    else:
        return JsonResponse({"error": "Method not allowed"}, status=405)


@csrf_exempt
@login_required
def question_api(request, exam_id, question_id):
    user = request.user
    exam = Exam.objects.get(pk=exam_id)
    question = Question.objects.get(pk=question_id)

    if request.method == "GET":
        student_exam = StudentExam.objects.get(user=user, exam=exam)
        if not student_exam:
            return JsonResponse(
                {
                    "success": False,
                    "error": "You havent started the exam at all",
                    "code": 414,
                }
            )

        try:
            options = [option.text for option in question.options.all()]
            response = QResponse.objects.get(
                student_exam=student_exam, question=question
            )
        except QResponse.DoesNotExist:
            return JsonResponse(
                {
                    "success": True,
                    "question_text": question.text,
                    "options": options,
                }
            )

        return JsonResponse(
            {
                "success": True,
                "question_text": question.text,
                "options": options,
                "selected_option": response.selected_option.text,
            }
        )
    elif request.method == "POST":
        option_id = request.POST.get("option_id")
        if not option_id:
            return JsonResponse(
                {
                    "success": False,
                    "error": "Option ID is required",
                },
                status=400,
            )
        student_exam = StudentExam.objects.get(user=user, exam=exam)
        option = Option.objects.get(pk=option_id)

        response, created = QResponse.objects.get_or_create(
            student_exam=student_exam, question=question
        )
        response.selected_option = option
        response.save()

        return JsonResponse(
            {
                "success": True,
                "message": "Response saved successfully",
            }
        )
    else:
        return JsonResponse({"error": "Method not allowed"}, status=405)
