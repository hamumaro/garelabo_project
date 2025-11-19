# APIロジック用


from django.http import HttpResponse
from django.shortcuts import render

def test_view(request):
    return HttpResponse("API is working!")

def list_page_view(request):
    return render(request, 'List.html')

def favorite_page_view(request):
    return render(request, 'Favorite_List.html')

def login_page_view(request):
    return render(request, 'login.html')