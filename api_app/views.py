# APIロジック用


from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import LoginForm

def test_view(request):
    return HttpResponse("API is working!")


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('login')
    else:
        form = LoginForm()
    return render(request, "login.html")