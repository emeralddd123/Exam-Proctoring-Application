from functools import wraps
from django.shortcuts import redirect, render
from django.urls import reverse
from jwt import ExpiredSignatureError, InvalidTokenError, decode
from django.conf import settings


def token_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if "token" not in request.session:
            return redirect(reverse("login"))

        token = request.session["token"]

        try:
            data = decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            request.user = data
        except ExpiredSignatureError:
            return render(request, "error.html", {"message": "Token has expired"})
        except InvalidTokenError:
            return render(request, "error.html", {"message": "Invalid token"})

        return view_func(request, *args, **kwargs)

    return wrapper
