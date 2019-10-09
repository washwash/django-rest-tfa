from django.http import HttpResponse
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required


@login_required
def dummy_view(request):
    return HttpResponse(status=200)


def login_view(request):
    user = authenticate(
        request, 
        username=request.POST['username'],
        password=request.POST['password']
    )
    if user:
        login(request, user)
        return HttpResponse(status=200)
    return HttpResponse(status=403)

