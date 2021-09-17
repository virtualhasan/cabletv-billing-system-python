from django.http.response import HttpResponse
from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, login, logout


# Create your views here.
def login_view(request):
    username = request.POST.get('username')
    password = request.POST.get('password')
    
    if request.user.is_authenticated:
        return redirect('/')

    if request.method == 'POST':
        user = authenticate(request, username=username, password=password)

        if user is None:
            return render(request,'accounts/login.html',{'error':'Username Or Password Wrong'})
        
        login(request, user)
        return redirect(request.GET.get('next'))

    

    return render(request, 'accounts/login.html', {})


def logout_view(request):
    logout(request)
    return redirect('/')