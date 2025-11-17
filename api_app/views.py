# APIロジック用


from django.http import HttpResponse

def test_view(request):
    return HttpResponse("API is working!")
