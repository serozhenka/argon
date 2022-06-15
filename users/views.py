from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import user_passes_test, login_required
from django.shortcuts import render, redirect

from .forms import LoginForm, RegisterForm

@user_passes_test(lambda user: not user.is_authenticated, login_url='/', redirect_field_name=None)
def login_page(request):
    context = {
        'page': 'login',
    }
    if request.method == "GET":
        context['form'] = LoginForm()
    elif request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password'],
            )
            if user:
                login(request, user)
                return redirect('/')

        context['form'] = form

    return render(request, 'users/login_register.html', context=context)

@user_passes_test(lambda user: not user.is_authenticated, login_url='/', redirect_field_name=None)
def register_page(request):
    context = {
        'page': 'register',
    }
    if request.method == "GET":
        context['form'] = RegisterForm()
    elif request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('/')

        context['form'] = form

    return render(request, 'users/login_register.html', context=context)

@login_required(login_url='login/')
def logout_page(request):
    logout(request)
    return redirect('/')

@login_required(login_url='login/')
def feed_page(request):
    return render(request, 'feed.html')