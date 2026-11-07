
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:
            login(request, user)
            return redirect("dashboard")

        messages.error(request, "Invalid username or password")

    return render(request, "core/login.html")
def dashboard_view(request):
    if not request.user.is_authenticated:
        return redirect("login")

    return render(request, "core/dashboard.html")
def logout_view(request):
    if request.method == "POST":
        logout(request)

    return redirect("login")