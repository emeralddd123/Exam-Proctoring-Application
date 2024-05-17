from celery import shared_task, app, Celery
from django.shortcuts import get_object_or_404
import numpy as np
from PIL import Image as PilImage
from django.contrib.auth import get_user_model
from face_recog.celery import app
from exams.models import CapturedImage, Exam, StudentExam
from users.face import encode_and_compare_faces, face_check
from users.models import Image



User = get_user_model()

@app.task
def face_rec_task(exam_id, user_id, image_id):
    print('task_called')
    exam = get_object_or_404(Exam, pk=exam_id)
    user = get_object_or_404(User, pk=user_id)
    
    captured_image = CapturedImage.objects.get(pk=image_id)
    image_np_array = np.asarray(PilImage.open(captured_image.image_data))
    face_in_image = face_check(image_np_array)


    if not face_in_image:
        captured_image.is_match = False
        return 'no image captured'

    user_images = Image.objects.filter(user=user)
    user_images_np = [np.array(PilImage.open(image.image)) for image in user_images]

    face_match = encode_and_compare_faces(
        input_face=image_np_array, user_faces=user_images_np
    )
    
    print('is_face_match:', face_match)
    if face_match:
        captured_image.is_match = True
        
        captured_image.save()
        return face_match
    else: return face_match
