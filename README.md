# Online Exam Anti Cheating System

## Overview

The Online Exam Anti Cheating system is designed to ensure the integrity and security of online exams by implementing face recognition technology at various stages of the exam process. The system requires users to register with at least 5 images of themselves, which are used for face recognition during login and throughout the exam.

## Features

1. **Signup**: Users are required to register with at least 5 images of themselves. These images serve as reference points for face recognition.
2. **Login**: Registered users can access the system using face recognition. Access to the exam interface is granted only after successful face recognition.
3. **Exam Verification**:
   - **Start**: Face recognition is required at the beginning of the exam to verify the identity of the user.
   - **Middle**: During the exam, users may be prompted for face recognition at random intervals to ensure the same person is taking the exam. If the face recognition fails, the user can continue with the exam, but the system will record the discrepancy.
   - **End**: Face recognition is required at the end of the exam to verify the identity of the user and confirm completion. Any discrepancies in face recognition will be recorded for administrator review.
4. **Admin Panel**: Administrators have access to exam data and can review face recognition records to identify any discrepancies.

## Usage

1. **Signup Process**:
   - Users must provide at least 5 images of themselves during registration.
   - Images should capture various facial expressions and angles to improve face recognition accuracy.

2. **Login and Exam Access**:
   - After registration, users can access the system using face recognition.
   - Access to the exam interface is granted only after successful face recognition.

3. **Exam Verification**:
   - At the start, middle, and end of the exam, users may be prompted for face recognition.
   - Face recognition ensures the integrity of the exam by verifying the identity of the user.
   - In case of a discrepancy in face recognition during the middle or end of the exam, users can continue with the exam, but the system will record the discrepancy for administrator review.

4. **Admin Review**:
   - Administrators have access to exam data and face recognition records.
   - They can review records to identify any discrepancies or instances of suspected cheating.

## Notes

- The system is designed to enhance exam security but may not be perfect.
- Users should ensure proper lighting and visibility during face recognition to minimize errors.
- Administrators play a crucial role in reviewing exam data and ensuring the integrity of the exam process.

### Sharing the Environment

- the `environment.yml` should help with installation of the requirements
- command to update it is `conda env export > environment.yml`

### Recreating the Environment

- to recreate, navigate to the directory of the environment. and `conda env create -f environment.yml`
- activate the environment with `conda activate your_environment_name`

### Creating SuperUser/Admin

- run `python manage.py createsuperuser`
- then you can head up to `localhost:8000\admin` to access the admin panel, that's where the admin features are located
like setting questions, exams, reviewing flagged user's face.

### Running the project

- the face recogniton model is being run by background workers using celery, this takes
the processing load off the main server thread
- use the command `python manage.py runserver` to start the project, and
- use the command `celery -A face_recog worker --loglevel=info` to start the workers
