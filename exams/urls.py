from django.urls import path


from . import views

app_name = "exams"

urlpatterns = [
    path("", views.index, name="index"),
    path("exams", views.list_exams, name="exams"),
    path("<int:exam_id>/", views.view_exam, name="view_exam"),
    path("start_exam/<int:exam_id>", views.start_exam, name="start_exam"),
    path("<int:exam_id>/question", views.exam_question, name="exam_question"),
    # path(
    #     "mid_exam/verify/<int:exam_id>",
    #     views.mid_exam_verification,
    #     name="mid_exam_verification",
    # ),
    path(
        "end_exam/verify/<int:exam_id>",
        views.end_exam_verification,
        name="end_exam_verification",
    ),
    path(
        "result/<int:exam_id>",
        views.end_exam_result,
        name="end_exam_result",
    ),
    path("start_exam/<int:exam_id>/", views.start_exam_api, name="start_exam_api"),
    path(
        "exam_verification/<int:exam_id>/",
        views.exam_verification_api,
        name="exam_verification_api",
    ),
    path(
        "question/<int:exam_id>/<int:question_id>/",
        views.question_api,
        name="question_api",
    ),
]
