from django.urls import path
from django.views.decorators.csrf import csrf_exempt


from . import views

app_name = 'users'

urlpatterns = [
    path("", views.index, name="index"),
    path("signup", views.signup, name="signup"),
    path("login", views.login_view, name="login"),
    path("face_rec", csrf_exempt(views.face_rec_view), name="face_rec"),
    path("dashboard", views.dashboard, name="dashboard"),
    path("home", views.home, name="home"),
    path("logout/", views.logout_view, name="logout"),
]
