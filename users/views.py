from django.http import HttpResponseBadRequest, HttpRequest, HttpResponseRedirect, HttpResponseServerError
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import login, authenticate, get_user_model, logout
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from .forms import UserCreationForm as SignUpForm, LoginForm
from .models import Image
from django.contrib import messages
from .face import encode_and_compare_faces


from PIL import Image as PilImage
import numpy as np

User = get_user_model()


def index(request):
    return "User App"


def signup(request):
    if request.method == "POST":
        form = SignUpForm(request.POST, request.FILES)
        if form.is_valid():
            print(f"form is valid")
            username = form.cleaned_data["username"]
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password1"]
            images = request.FILES.getlist("images")  # Get the list of uploaded images

            # Create the user
            user = User.objects.create_user(
                username=username, email=email, password=password
            )

            # Create Image instances for each uploaded image and associate them with the user
            for image in images:
                Image.objects.create(user=user, image=image)

            # Log in the user
            # login(request, user, 'users.backends.EmailAuthBackend')
            return redirect("users:login")
        else:
            print("invalid form")
    else:
        form = SignUpForm()
    return render(request, "signup.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]
            user = authenticate(request, email=email, password=password)

            if user is not None:
                login(request, user, 'users.backends.EmailAuthBackend')
                return redirect("exams:exams")
            else:
                messages.error(request, "Invalid email or password.")
    else:
        form = LoginForm()
    return render(request, "login.html", {"form": form})


def face_rec_view(request):
    if "user_id" not in request.session:
        return redirect("login")

    if request.method == "POST":
        input_face = request.FILES.get("image", None)

        if not input_face:
            messages.error(request, "Please provide face info by capturing an image")
            return HttpResponseBadRequest(
                "Please provide face info by capturing an image"
            )

        # Trying to convert the image to np_array
        img = PilImage.open(input_face)
        img_np = np.array(img)

        user_id = request.session["user_id"]
        user = User.objects.get(id=user_id)

        user_images = Image.objects.filter(user=user)
        user_images_np = [np.array(PilImage.open(image.image)) for image in user_images]

        face_match = encode_and_compare_faces(
            input_face=img_np, user_faces=user_images_np
        )
        print("face_match :", face_match)
        if face_match:
            login(request, user, 'users.backends.EmailAuthBackend')
            return redirect(to='/exams/exams')
        else:
            error_message = "Face recognition failed. Please ensure your face is well-lit and unobstructed."
            messages.error(request, error_message)
            return HttpResponseRedirect(request.path)

    return render(request, "face_recognition.html")


@login_required(login_url="login")
def dashboard(request):  #
    user = request.user
    print(user)
    return render(request, "dashboard.html", {"user": user})


def home(request):
    return render(request, "home.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(
            reverse("users:login")
        )
