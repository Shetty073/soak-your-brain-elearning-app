from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import Group
from django.shortcuts import render, redirect

from ..decorators import allowed_users
from ..models import *


@login_required
@allowed_users(allowed_roles=['sybadmin'])
def syb_admin_page(request):
    plans = Plan.objects.all()
    colleges = College.objects.all()
    invoices = Invoice.objects.all()
    syb_admin_users = User.objects.filter(groups__name='sybadmin')

    total_amount_paid_till_date = 0.0

    for invoice in invoices:
        total_amount_paid_till_date += float(invoice.amount_paid)

    total_no_plans = Plan.objects.count()
    total_no_colleges = College.objects.count()
    total_no_students = Student.objects.count()
    total_no_teachers = Teacher.objects.count()

    context_dict = {
        'plans': plans,
        'colleges': colleges,
        'invoices': invoices,
        'total_amount_paid_till_date': total_amount_paid_till_date,
        'total_no_plans': total_no_plans,
        'total_no_colleges': total_no_colleges,
        'total_no_students': total_no_students,
        'total_no_teachers': total_no_teachers,
        'syb_admin_users': syb_admin_users,
    }
    return render(request, template_name='sybadmin/dashboard/dashboard.html', context=context_dict)


@login_required
@allowed_users(allowed_roles=['sybadmin'])
def add_admin_users(request):
    if request.method == 'POST':
        if request.user.is_superuser:
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            email = request.POST.get('email')
            password = request.POST.get('password')
            confirm_password = request.POST.get('confirm_password')
            is_superuser = request.POST.get('is_superuser')

            if password != confirm_password:
                messages.error(request=request, message='Passwords do not match')
                return redirect(add_admin_users)

            if is_superuser == 'on':
                is_superuser = True
            else:
                is_superuser = False

            user = User.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                email=email,
                username=email,
            )
            user.set_password(password)
            user.is_staff = is_superuser
            user.is_superuser = is_superuser
            user.save()

            collegeadmin_group = Group.objects.get(name='sybadmin')
            collegeadmin_group.user_set.add(user)

            return redirect(syb_admin_page)

    if request.user.is_superuser:
        return render(request, template_name='sybadmin/dashboard/add_admin_users.html')
    else:
        redirect(syb_admin_page)


@login_required
@allowed_users(allowed_roles=['sybadmin'])
def syb_admin_account(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_new_password = request.POST.get('confirm_new_password')

        user = request.user
        if check_password(current_password, user.password):
            if first_name != user.first_name:
                user.first_name = first_name
            if last_name != user.last_name:
                user.last_name = last_name
            if email != user.email:
                user.email = email

            if new_password.strip() != '':
                if new_password == confirm_new_password:
                    user.set_password(new_password)
                else:
                    messages.error(request=request, message='Passwords do not match! Please try again.')
                    return redirect(syb_admin_account)

            user.save()
            messages.success(request=request, message='Changes saved successfully!')
            return redirect(syb_admin_account)

        else:
            messages.error(request=request, message='Current password you entered is incorrect.')
            return redirect(syb_admin_account)

    return render(request, template_name='sybadmin/dashboard/syb_admin_account.html')


@login_required
@allowed_users(allowed_roles=['sybadmin'])
def view_update_college_details(request, pk=None):
    if request.method == 'POST':
        college = College.objects.get(pk=pk)
        user = college.user

        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        college_name = request.POST.get('college_name')
        email = request.POST.get('email')
        phone_no = request.POST.get('phone_no')
        plan_subscribed_id = request.POST.get('plan_subscribed')
        plan_subscribed = Plan.objects.get(pk=plan_subscribed_id)
        subscription_start_date = request.POST.get('subscription_start_date')
        subscription_end_date = request.POST.get('subscription_end_date')
        subscription_active = request.POST.get('subscription_active')

        if subscription_active == 'on':
            subscription_active = True
        else:
            subscription_active = False

        if first_name != college.first_name:
            college.first_name = first_name
            user.first_name = first_name
        if last_name != college.last_name:
            college.last_name = last_name
            user.last_name = last_name
        if college_name != college.college_name:
            college.college_name = college_name
        if email != college.email:
            college.email = email
            user.email = email
            user.username = email
        if phone_no != college.phone_no:
            college.phone_no = phone_no
        if plan_subscribed != college.plan_subscribed:
            college.plan_subscribed = plan_subscribed
        if subscription_start_date != college.subscription_start_date:
            college.subscription_start_date = subscription_start_date
        if subscription_end_date != college.subscription_end_date:
            college.subscription_end_date = subscription_end_date
        if subscription_active != college.subscription_active:
            college.subscription_active = subscription_active

        college.save()
        user.save()

        return redirect(syb_admin_page)

    college = None
    plans = None

    try:
        college = College.objects.get(pk=pk)
    except Exception as err:
        college = None

    try:
        plans = Plan.objects.all()
    except Exception as err:
        plans = None

    context_dict = {
        'college': college,
        'plans': plans,
    }
    return render(request, template_name='sybadmin/dashboard/view_college_details.html', context=context_dict)


@login_required
@allowed_users(allowed_roles=['sybadmin'])
def view_invoice_details(request, pk=None):
    invoice = None
    try:
        invoice = Invoice.objects.get(pk=pk)
    except Exception as err:
        invoice = None

    context_dict = {
        'invoice': invoice,
    }
    return render(request, template_name='sybadmin/dashboard/view_invoice_details.html', context=context_dict)
