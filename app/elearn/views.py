from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from .decorators import unauthenticated_user, allowed_users
from .models import *


# Views and endpoints
def home(request):
    context_dict = {}
    return render(request, template_name='home.html', context=context_dict)


def sign_up(request):
    if request.method == "POST":
        print(request.POST.get("name"))
        return HttpResponse("Do something")
    context_dict = {}
    return render(request, template_name='sign_up.html', context=context_dict)


def sign_in(request):
    context_dict = {}
    return render(request, template_name='sign_in.html', context=context_dict)


def checkout_page(request):
    context_dict = {}
    return render(request, template_name='checkout/checkbout.html', context=context_dict)


def admin_page(request):
    context_dict = {}
    return render(request, template_name='administration/admin.html', context=context_dict)


def college_page(request):
    context_dict = {}
    return render(request, template_name='college/college_base.html', context=context_dict)
