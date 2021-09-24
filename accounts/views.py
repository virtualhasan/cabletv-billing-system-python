from django.http.response import HttpResponse
from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import PasswordChangeForm

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


@login_required
def profile_view(request):
    
    return render(request, 'accounts/profile.html',{})

@login_required
def logout_view(request):
    logout(request)
    return redirect('/')

@login_required
def password_change_view(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            return redirect('accounts:profile')
        else:
            print("invalid")

        return render(request, 'accounts/password_change.html', {'form':form})
    
    form = PasswordChangeForm(request.user)

    return render(request, 'accounts/password_change.html', {'form':form})