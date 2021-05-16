import json

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import Group
from django.core.validators import validate_email
from django.db import IntegrityError
from django.http import JsonResponse
from django.shortcuts import render, redirect

from ..decorators import unauthenticated_user
from ..models import *

from .college_views import *
from .sybadmin_views import *
from .teacher_views import *
from .student_views import *


# Views and endpoints
def home(request):
    plans = Plan.objects.all()
    context_dict = {
        'plans': plans,
    }
    return render(request, template_name='home.html', context=context_dict)


@unauthenticated_user
def sign_up(request, plan_subscribed=''):
    if request.method == 'POST':
        data = json.loads(request.body)
        first_name = data['first_name']
        last_name = data['last_name']
        college_name = data['college_name']
        email_id = data['email_id']
        password1 = data['password']
        phone_no = data['phone_no']
        card_no = data['card_no']
        card_cvv = data['card_cvv']
        plan_subscribed = data['plan_subscribed']

        # Process payment
        # This is just dummy code because I am not going to implement any actual
        # payment processing for this project
        pay_status_failed = False
        if pay_status_failed:
            return redirect(payment_failed)

        try:
            # register the User
            new_user = User.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                email=email_id,
                username=email_id,
            )
            new_user.set_password(password1)
            new_user.save()

            # Add this user to collegeadmin group
            collegeadmin_group = Group.objects.get(name='collegeadmin')
            collegeadmin_group.user_set.add(new_user)

            # get the plan_subscribed object
            plan = Plan.objects.get(name=plan_subscribed)

            # register the User as College
            college = College.objects.create(
                user=new_user,
                plan_subscribed=plan,
                first_name=first_name,
                last_name=last_name,
                college_name=college_name,
                email=email_id,
                phone_no=phone_no,
                card_info=card_no,
            )
            college.set_initial_subscription_dates()
            college.save()

            # NOTE: Here you can add backend payment processing
            # process the payment here and generate invoice for it
            invoice = Invoice.objects.create(
                college=college,
                plan_subscribed=plan,
            )
            invoice.pay()
            invoice.save()

            # Now log the user in
            auth_user = authenticate(request, username=email_id, password=password1)
            if auth_user is not None:
                login(request, auth_user)
                return JsonResponse({'process': 'success'})
            else:
                return JsonResponse({'process': 'failed', 'msg': 'User authentication system failed! Please sign in'})
        except IntegrityError:
            return JsonResponse({'process': 'failed', 'msg': 'User already exists'})
        except Exception as err:
            return JsonResponse({'process': 'failed', 'msg': f'{str(err)}'})

    plans = Plan.objects.all().values_list('name', flat=True)
    if plan_subscribed not in plans:
        return redirect(home)
    cost_of_selected_plan = Plan.objects.get(name=plan_subscribed).price_per_year
    context_dict = {'plan_selected': plan_subscribed, 'plan_cost': f'₹{int(cost_of_selected_plan)} / year'}
    return render(request, template_name='sign_up.html', context=context_dict)


@unauthenticated_user
def sign_in(request):
    if request.method == 'POST':
        username = request.POST.get('email')  # username and email are one and the same for the context of this app
        password = request.POST.get('password')
        try:
            # Log the user in
            auth_user = authenticate(request, username=username, password=password)
            if auth_user is not None:
                login(request, auth_user)
                # Now redirect based on what group user is a part of
                login_user = User.objects.get(username=username)
                login_user_group = login_user.groups.all()[0].name
                redirect_dict = {
                    'collegeadmin': college_page,
                    'teacher': college_teacher,
                    'student': college_student,
                    'sybadmin': syb_admin_page,
                }
                return redirect(redirect_dict[login_user_group])
            else:
                if User.objects.filter(username=username).exists():
                    context_dict = {'msg': 'Email id or password is wrong'}
                    return render(request, template_name='sign_in.html', context=context_dict)

                context_dict = {'msg': 'User does not exist please sign up first'}
                print(1)
                return render(request, template_name='sign_in.html', context=context_dict)
        except Exception as err:
            context_dict = {'msg': f'{err}'}
            return render(request, template_name='sign_in.html', context=context_dict)
    context_dict = {}
    return render(request, template_name='sign_in.html', context=context_dict)


def sign_out(request):
    # sign out logic here
    logout(request)
    context_dict = {'msg': 'Logged out successfully'}
    return render(request, template_name='sign_in.html', context=context_dict)


def checkout_page(request):
    context_dict = {}
    return render(request, template_name='checkout/checkbout.html', context=context_dict)


@login_required
def user_password_reset(request):
    """
        This is for resetting password of users
        :param request:
        :return:
    """
    if request.method == 'POST':
        go_back_path = request.POST.get('full_path')
        current_password_entered = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_new_password = request.POST.get('confirm_new_password')

        user = User.objects.get(pk=request.user.pk)

        if check_password(current_password_entered, user.password):
            if new_password == confirm_new_password:
                if 8 <= len(new_password) <= 16:
                    user.set_password(new_password)
                    user.save()
                    msg = 'Password changed successfully'
                    messages.success(request, f'{msg}')
                    return redirect(go_back_path)
                else:
                    err = 'Password must be 8 to 16 characters long'
                    messages.error(request, f'{err}')
                    return redirect(go_back_path)
            else:
                err = 'Passwords do not match'
                messages.error(request, f'{err}')
                return redirect(go_back_path)
        else:
            err = 'Current password entered is incorrect'
            messages.error(request, f'{err}')
            return redirect(go_back_path)

    return JsonResponse({
        'process': 'failed',
        'msg': 'GET method not supported'
    })


@login_required
def user_info_change(request):
    """
        This is for updating email, first_name and last_name of users
        :param request:
        :return:
    """
    if request.method == 'POST':
        go_back_path = request.POST.get('full_path')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')

        user = request.user
        teacher = None
        student = None
        college = None

        try:
            teacher = request.user.teacher
        except Exception as err:
            teacher = None

        try:
            student = request.user.student
        except Exception as err:
            student = None

        try:
            college = request.user.college
        except Exception as err:
            college = None

        try:
            validate_email(email)
        except Exception as err:
            messages.error(request, f'{err}')
            return redirect(go_back_path)

        if first_name.isalpha():
            user.first_name = first_name
            user.last_name = last_name
            user.email = email
            user.username = email
            user.save()

            if teacher is not None:
                teacher.email = email
                teacher.first_name = first_name
                teacher.last_name = last_name
                teacher.save()

            if student is not None:
                student.email = email
                student.first_name = first_name
                student.last_name = last_name
                student.save()

            if college is not None:
                college.email = email
                college.first_name = first_name
                college.last_name = last_name
                college.save()

            msg = 'Your details had been changed successfully'
            messages.success(request, f'{msg}')
            return redirect(go_back_path)
        else:
            err = 'Name cannot contain numbers in it'
            messages.error(request, f'{err}')
            return redirect(go_back_path)

    return JsonResponse({
        'process': 'failed',
        'msg': 'GET method not supported'
    })


def payment_failed(request):
    return render(request, template_name='payment_failed.html')
