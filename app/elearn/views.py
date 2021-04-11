import json

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import Group
from django.core.validators import validate_email
from django.db import IntegrityError
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.utils.html import escape

from .decorators import unauthenticated_user, allowed_users
from .models import *


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


@login_required
@allowed_users(allowed_roles=['collegeadmin'])
def college_page(request):
    teachers = Teacher.objects.filter(college=request.user.college)
    departments = Department.objects.filter(college=request.user.college)
    classes = CollegeClass.objects.filter(college=request.user.college)
    students = Student.objects.filter(college=request.user.college)

    class_assignments = [assignment for assignment in ClassWorkPost.objects.filter(is_assignment=True) if assignment.college_class in classes]
    total_number_of_assignments = len(class_assignments)

    submitted_assignments = [solution for solution in AssignmentSolution.objects.all() if solution.student in students]
    number_of_submitted_assignments = len(submitted_assignments)

    context_dict = {
        'teachers': teachers,
        'departments': departments,
        'classes': classes,
        'students': students,
        'total_number_of_assignments': total_number_of_assignments,
        'number_of_submitted_assignments': number_of_submitted_assignments,
        'number_of_students': len(students),
        'number_of_teachers': len(teachers),
    }
    return render(request, template_name='college/admin/college_admin.html', context=context_dict)


@login_required
def renew_plan(request):
    # We cannot use allowed_users decorator for this view because
    # using that decorator will force the user to plan_cancelled
    # view and refrain him/her from renewing the subscription plan.
    if request.user.groups.all()[0].name == 'collegeadmin':
        if request.method == 'POST':
            plan_selected = request.POST.get('plan_selected')
            cardnumber = request.POST.get('cardnumber')
            cardnumber = cardnumber.replace(' ', '')
            cardcvv = request.POST.get('cardcvv')
            plan = None

            try:
                plan = Plan.objects.get(pk=plan_selected)
            except Exception as err:
                messages.error(request, f'{err}')
                return redirect(renew_plan)

            college = request.user.college
            college.renew(plan=plan, card_info=cardnumber)
            college.save()

            # NOTE: Here you can add backend payment processing
            # process payments here and generate invoice
            invoice = Invoice.objects.create(
                college=request.user.college,
                plan_subscribed=plan,
            )
            invoice.pay()
            invoice.save()

            return redirect(college_admin_account)

        if request.user.college.days_left() > 15 and request.user.college.subscription_active:
            return redirect(college_admin_account)

        plans = Plan.objects.all()
        context_dict = {
            'plans': plans,
        }
        return render(request, template_name='college/admin/renew_plan.html', context=context_dict)
    else:
        return HttpResponse('You are not authorized to view this page')


@login_required
@allowed_users(allowed_roles=['collegeadmin'])
def cancel_plan(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        college_id = data['college_id']
        college = College.objects.get(pk=college_id)

        if college.subscription_end_date < datetime.now().date():
            return JsonResponse({
                'process': 'failed',
                'msg': 'Your plan is not active. Please renew your plan in order to continue using our product.',
            })

        college.cancel_plan()
        college.save()

        return JsonResponse({
            'process': 'success',
            'msg': 'Your plan/subscription has been deactivated. '
                   'Please renew your plan in order to continue using our product.',
        })

    return JsonResponse({
        'process': 'failed',
        'msg': 'GET method is not supported by this endpoint',
    })


@login_required
def plan_cancelled(request):
    # We cannot use allowed_users decorator for this view because
    # using that will generate a redirection infinite loop and we
    # will get the error of 'too many redirects'.
    if request.user.groups.all()[0].name == 'collegeadmin':
        if not request.user.college.subscription_active or request.user.college.days_left() < 1:
            return render(request, template_name='college/admin/plan_cancelled.html')
        else:
            return redirect(college_admin_account)
    elif request.user.groups.all()[0].name == 'teacher':
        if not request.user.teacher.college.subscription_active or request.user.teacher.college.days_left() < 1:
            return render(request, template_name='college/admin/plan_cancelled.html')
        else:
            return redirect(college_teacher_student_account)
    elif request.user.groups.all()[0].name == 'student':
        if not request.user.student.college.subscription_active or request.user.student.college.days_left() < 1:
            return render(request, template_name='college/admin/plan_cancelled.html')
        else:
            return redirect(college_teacher_student_account)
    else:
        return HttpResponse('You are not authorized to view this page')


@login_required
@allowed_users(allowed_roles=['collegeadmin'])
def college_add_teachers(request, pk=None):
    classes_list = [classname['name'] for classname in
                    CollegeClass.objects.filter(college=request.user.college).values('name')]
    if request.method == 'POST':
        # for AJAX request
        data = json.loads(request.body)
        mode = data['mode']
        first_name = data['first_name']
        last_name = data['last_name']
        classes_assigned = data['classes_assigned']
        email_id = data['email_id']
        password1 = None if data['password1'] == '' else data['password1']

        if mode == 'add':
            # request is for adding new teacher
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

                # Add this user to teacher group
                collegeadmin_group = Group.objects.get(name='teacher')
                collegeadmin_group.user_set.add(new_user)

                # Get the college of the current logged in user (collegeadmin user)
                college = request.user.college

                # create a teacher
                clg_teacher = Teacher.objects.create(
                    user=new_user,
                    college=college,
                    first_name=first_name,
                    last_name=last_name,
                    email=email_id,
                )

                # add the assigned classes to this teacher
                for cls in classes_assigned:
                    clg_cls = CollegeClass.objects.get(name=cls, college=request.user.college)
                    clg_teacher.college_classes.add(clg_cls)

                return JsonResponse({
                    'process': 'success',
                    'msg': f'Success! Teacher {first_name} {last_name} has been added to the database.',
                })
            except IntegrityError:
                return JsonResponse({
                    'process': 'failed',
                    'msg': f'Teacher {first_name} {last_name} has already been added to the database.'
                })
            except Exception as err:
                return JsonResponse({'process': 'failed', 'msg': f'{err}'})
        else:
            # this is an AJAX request for updating existing teacher
            # This request also will contain password2 field data as password validation is
            # not done on client side for this request's form
            password2 = None if data['password2'] == '' else data['password2']
            try:
                # Get the teacher by pk (id) and update the data
                clg_teacher_id = data['teacher_id']
                clg_teacher = Teacher.objects.get(pk=clg_teacher_id, college=request.user.college)
                clg_teacher.first_name = first_name
                clg_teacher.last_name = last_name
                clg_teacher.email = email_id

                # Now update the User associated (OneToOne) with the Teacher
                clg_teacher.user.email = email_id
                clg_teacher.user.username = email_id
                clg_teacher.user.first_name = first_name
                clg_teacher.user.last_name = last_name

                # Update the classes assigned to the teacher
                # First clear existing classes data
                clg_teacher.college_classes.clear()
                # Now add newly selected/edited data
                for cls in classes_assigned:
                    clg_cls = CollegeClass.objects.get(name=cls, college=request.user.college)
                    clg_teacher.college_classes.add(clg_cls)

                # if the password provided is valid then update it too
                if password1 is not None and password2 is not None:
                    if password1 == password2:
                        clg_teacher.user.set_password(password1)
                    else:
                        return JsonResponse({
                            'process': 'failed',
                            'msg': f'Error! passwords do not match',
                        })

                # Now save the data
                clg_teacher.user.save()
                clg_teacher.save()

                # updated_teacher_data is for updating the html table in the frontend once
                # request gets processed
                updated_teacher_data = {
                    'id': clg_teacher.id,
                    'first_name': clg_teacher.first_name,
                    'last_name': clg_teacher.last_name,
                    'email_id': clg_teacher.email,
                    'class_list': [cls_name.name for cls_name in clg_teacher.college_classes.all()],
                }

                # Return success message
                return JsonResponse({
                    'process': 'success',
                    'msg': f'{first_name} {last_name}\'s data has been successfully updated.',
                    'updated_data': updated_teacher_data,
                })
            except Exception as err:
                return JsonResponse({
                    'process': 'failed',
                    'msg': f'Error! {err}',
                })
    if pk is not None:
        # it means that this is an AJAX GET request for getting a teacher's data using pk (id)
        try:
            teacher = Teacher.objects.get(pk=pk, college=request.user.college)
            teacher_json_obj = {
                'first_name': teacher.first_name,
                'last_name': teacher.last_name,
                'classes_assigned': [teach.name for teach in teacher.college_classes.all()],
                'email_id': teacher.email,
            }
            return JsonResponse({
                'process': 'success',
                'msg': 'Success',
                'teacher_json_obj': teacher_json_obj,
            })
        except Exception as err:
            return JsonResponse({
                'process': 'failed',
                'msg': f'Error! {err}',
            })

    context_dict = {'classes_list': classes_list}
    return render(request, template_name='college/admin/admin_addteachers.html', context=context_dict)


@login_required
@allowed_users(allowed_roles=['collegeadmin'])
def college_del_teachers(request, pk=None):
    """
    This view is for handling AJAX requests only for deleting teachers.
    :param request:
    :param pk:
    :return: JsonResponse()
    """
    if request.method == 'POST':
        try:
            teacher = Teacher.objects.get(pk=pk, college=request.user.college)
            teacher.delete()
            return JsonResponse({'process': 'success'})
        except Exception as err:
            return JsonResponse({'process': 'failed', 'msg': f'{err}'})

    return JsonResponse({'process': 'failed', 'msg': 'Error! invalid operation'})


@login_required
@allowed_users(allowed_roles=['collegeadmin'])
def college_add_classes(request, pk=None):
    departments_list = [department['name'] for department in
                        Department.objects.filter(college=request.user.college).values('name')]
    if request.method == 'POST':
        # for AJAX request
        data = json.loads(request.body)
        form_type = data['form_type']
        if form_type == 'department':
            if pk is None:
                # this means that the request came from 'add new department' form
                department_name = data['department_name']
                college = request.user.college
                try:
                    obj, created = Department.objects.get_or_create(
                        college=college,
                        name=department_name,
                    )

                    if not created:
                        return JsonResponse({
                            'process': 'failed',
                            'msg': f'{department_name} department already exists in the the database.',
                        })

                    return JsonResponse({
                        'process': 'success',
                        'msg': f'Success! {department_name} department added to the database.',
                        'departments_list': departments_list,
                    })
                except IntegrityError:
                    return JsonResponse({'process': 'failed', 'msg': f'{department_name} already exists.'})
                except Exception as err:
                    return JsonResponse({'process': 'failed', 'msg': f'{err}'})
            else:
                # this request came for updating an existing department's fields
                department_name = data['department_name']
                try:
                    dep = Department.objects.get(pk=pk, college=request.user.college)
                    dep.name = department_name
                    dep.save()

                    return JsonResponse({
                        'process': 'success',
                        'department_name': f'{dep.name}',
                    })
                except IntegrityError:
                    return JsonResponse({
                        'process': 'failed',
                        'msg': 'Duplicate value error',
                    })
                except Exception as err:
                    return JsonResponse({
                        'process': 'failed',
                        'msg': f'{err}',
                    })
        elif form_type == 'class':
            if pk is None:
                # this means that the request came from 'add new classes' form
                class_name = data['class_name']
                department = Department.objects.get(name=data['department_name'], college=request.user.college)
                college = request.user.college
                try:
                    obj, created = CollegeClass.objects.get_or_create(
                        college=college,
                        name=class_name,
                        department=department,
                    )

                    if not created:
                        return JsonResponse({
                            'process': 'failed',
                            'msg': f'{class_name} class already exists under {department.name} department',
                            'departments_list': departments_list,
                        })

                    return JsonResponse({
                        'process': 'success',
                        'msg': f'Success! {class_name} class added under {department.name}',
                        'departments_list': departments_list,
                    })
                except IntegrityError:
                    return JsonResponse({'process': 'failed',
                                         'msg': f'{class_name} already exists under {department.name} department'})
                except Exception as err:
                    return JsonResponse({'process': 'failed', 'msg': f'{err}'})
            else:
                # this request came for updating an existing class's fields
                class_name = data['class_name']
                department_name = data['department_name']
                try:
                    cls = CollegeClass.objects.get(pk=pk)
                    cls.name = class_name
                    cls.department = Department.objects.get(name=department_name, college=request.user.college)
                    cls.save()

                    return JsonResponse({
                        'process': 'success',
                        'class_name': f'{cls.name}',
                        'department_name': f'{cls.department}',
                    })
                except IntegrityError:
                    return JsonResponse({
                        'process': 'failed',
                        'msg': 'Duplicate value error',
                    })
                except Exception as err:
                    return JsonResponse({
                        'process': 'failed',
                        'msg': f'{err}',
                    })
    context_dict = {
        'departments_list': departments_list,
    }
    return render(request, template_name='college/admin/admin_addclasses.html', context=context_dict)


@login_required
@allowed_users(allowed_roles=['collegeadmin'])
def college_del_classes(request, pk=None):
    """
    This view is for handling AJAX requests only for deleting classes.
    :param request:
    :param pk:
    :return: JsonResponse()
    """
    if request.method == 'POST':
        data = json.loads(request.body)
        form_type = data['form_type']

        if form_type == 'class':
            try:
                college = CollegeClass.objects.get(pk=pk, college=request.user.college)
                college.delete()
                return JsonResponse({'process': 'success'})
            except Exception as err:
                return JsonResponse({'process': 'failed', 'msg': f'{err}'})

        elif form_type == 'department':
            try:
                department = Department.objects.get(pk=pk, college=request.user.college)
                department_class_count = CollegeClass.objects.filter(college=request.user.college,
                                                                     department=department).count()
                if department_class_count > 0:
                    return JsonResponse({'process': 'failed',
                                         'msg': f'{department_class_count} classes are part of the {department.name} '
                                                'department. Please delete these classes first before deleting this '
                                                'department.'})
                department.delete()
                return JsonResponse({'process': 'success'})
            except Exception as err:
                return JsonResponse({'process': 'failed', 'msg': f'{err}'})

        return JsonResponse({'process': 'failed', 'msg': 'Error! invalid operation'})

    return JsonResponse({'process': 'failed', 'msg': 'Error! invalid operation'})


@login_required
@allowed_users(allowed_roles=['collegeadmin'])
def college_admin_account(request):
    plan = request.user.college.plan_subscribed
    allotted_sp = plan.allotted_storage_space / 1000 if plan.allotted_storage_space > 999 else plan.allotted_storage_space
    allotted_storage_space = f'{plan.allotted_storage_space / 1000} TB' if plan.allotted_storage_space > 999 else f'{plan.allotted_storage_space} GB'
    used_storage_space = request.user.college.used_storage_space
    storage_space_left = plan.allotted_storage_space - used_storage_space

    percent_space_used = (used_storage_space / allotted_sp) * 100

    days_left = request.user.college.days_left()

    renewable = True if request.user.college.days_left() <= 15 else False

    context_dict = {
        'allotted_storage_space': allotted_storage_space,
        'used_storage_space': f'{used_storage_space} GB',
        'storage_space_left': f'{storage_space_left} GB',
        'percent_space_used': percent_space_used,
        'renewable': renewable,
        'days_left': days_left,
    }
    return render(request, template_name='college/admin/college_admin_account.html', context=context_dict)


@login_required
@allowed_users(allowed_roles=['teacher'])
def college_teacher(request):
    try:
        classes_list = [cls for cls in request.user.teacher.college_classes.all()]
    except Exception as err:
        context_dict = {
            'classes_list': None,
        }
        return render(request, template_name='college/teacher/teacher.html', context=context_dict)

    context_dict = {
        'classes_list': classes_list,
    }
    return render(request, template_name='college/teacher/teacher.html', context=context_dict)


@login_required
@allowed_users(allowed_roles=['teacher'])
def college_teacher_add_subjects(request, pk=None):
    if request.method == 'POST':
        data = json.loads(request.body)
        if pk is None:
            # This request is just for adding new subject
            subject_name = data['subject_name']
            try:
                subject, created = Subject.objects.get_or_create(name=subject_name,
                                                                 college=request.user.teacher.college)

                if not created:
                    return JsonResponse({'process': 'failed', 'msg': f'Subject {subject_name} already exists'})

                return JsonResponse({'process': 'success', 'msg': f'Successfully added {subject.name} subject',
                                     'subject_name': subject.name, 'subject_id': subject.pk})
            except Exception as err:
                return JsonResponse({'process': 'failed', 'msg': f'{err}'})
        else:
            # This request is for assigning subjects to a class whose id is pk
            try:
                selected_subjects = [int(subject_id) for subject_id in data['selected_subjects']]

                cls = CollegeClass.objects.get(pk=pk)
                subjects = [subject for subject in Subject.objects.all() if subject.id in selected_subjects]
                prev_selected_subjects = [subject for subject in
                                          Subject.objects.filter(college=request.user.teacher.college) if
                                          subject in cls.subjects.all()]

                removed = 0
                # first remove freshly deselected subjects which were previously selected
                for subject in prev_selected_subjects:
                    if subject not in subjects:
                        removed += 1
                        cls.subjects.remove(subject)

                # Flag for checking the total number of new subjects selected
                added = 0

                # assign new subjects
                for subject in subjects:
                    if subject not in cls.subjects.all():
                        added += 1
                        cls.subjects.add(subject)

                msg = f'This subject is already assigned to {cls.name}' if len(
                    subjects) < 2 else f'These subjects are already assigned to {cls.name}'

                if removed != 0:
                    msg = f'{removed} subjects removed'

                if added == 0:
                    # No new subjects were selected
                    return JsonResponse({
                        'process': 'success',
                        'msg': msg
                    })

                cls.save()

            except Exception as err:
                return JsonResponse({'process': 'failed', 'msg': f'{err}'})

            return JsonResponse({
                'process': 'success',
                'msg': f'Successfully assigned {added} subjects to {cls.name}'
            })

    if request.method == 'GET' and pk is not None:
        # This request is for getting the list of assigned subjects for a particular class
        try:
            cls = CollegeClass.objects.get(pk=pk)
            subjects = [subject.id for subject in Subject.objects.filter(college=request.user.teacher.college) if
                        subject in cls.subjects.all()]
            json_response_body = {
                'process': 'success',
                'class': cls.id,
                'subjects': subjects,
            }
        except Exception as err:
            json_response_body = {
                'process': 'failed',
                'msg': f'{err}',
            }
            return JsonResponse(json_response_body)
        return JsonResponse(json_response_body)

    # This is a normal GET request for the page
    classes = request.user.teacher.college_classes.all()
    subjects = Subject.objects.filter(college=request.user.teacher.college)
    context_dict = {
        'classes': classes,
        'subjects': subjects,
    }
    return render(request, template_name='college/teacher/teacher_add_subjects.html', context=context_dict)


@login_required
@allowed_users(allowed_roles=['teacher'])
def college_teacher_add_students(request, pk=None):
    if request.method == 'POST':
        data = json.loads(request.body)
        if pk is None:
            # This is the POST request for adding a new student
            first_name = data['first_name']
            last_name = data['last_name']
            class_assigned = data['class_assigned']
            email_id = data['email_id']
            password1 = data['password1']

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

                # Add this user to the student group
                collegeadmin_group = Group.objects.get(name='student')
                collegeadmin_group.user_set.add(new_user)

                # get the class object from the id provided
                college_class = CollegeClass.objects.get(pk=class_assigned)
                college = request.user.teacher.college

                # create the student
                Student.objects.create(
                    user=new_user,
                    college=college,
                    college_class=college_class,
                    first_name=first_name,
                    last_name=last_name,
                    email=email_id
                )

            except IntegrityError:
                return JsonResponse({
                    'process': 'failed',
                    'msg': f'Student {first_name} {last_name} has already been added to the database.'
                })
            except Exception as err:
                return JsonResponse({'process': 'failed', 'msg': f'{err}'})

            return JsonResponse({'process': 'success', 'msg': 'Student successfully added to the database'})

    classes_list = request.user.teacher.college_classes.all()
    context_dict = {
        'classes_list': classes_list,
    }

    if request.method == 'GET' and pk is not None:
        # This is a GET request for this page along with the data for a particular student whose
        # id is pk.
        college_student = Student.objects.get(id=pk)
        context_dict = {
            'college_student': college_student
        }
        return render(request, template_name='college/teacher/teacher_add_students.html', context=context_dict)

    return render(request, template_name='college/teacher/teacher_add_students.html', context=context_dict)


@login_required
@allowed_users(allowed_roles=['teacher'])
def college_teacher_update_students(request, pk=None):
    # This view is responsible for updating and deleting a student
    if request.method == 'POST':
        data = json.loads(request.body)
        mode = data['mode']

        if mode == 'update':
            # This request is for updating the student
            first_name = data['first_name']
            last_name = data['last_name']
            class_assigned = data['class_assigned']
            email_id = data['email_id']
            password = data['password1']

            try:
                student = Student.objects.get(pk=pk)

                student.first_name = first_name
                student.last_name = last_name
                student.email = email_id
                student.college_class = CollegeClass.objects.get(pk=class_assigned)

                if password is not None and password != '':
                    student.user.set_password(password)

                student.save()
                return JsonResponse({'process': 'success', 'msg': 'Student details successfully updated!'})
            except Exception as err:
                return JsonResponse({'process': 'failed', 'msg': f'{err}'})

        else:
            # This request is for deleting the student
            student_id = data['student_id']
            try:
                student = Student.objects.get(pk=student_id)
                student.delete()
                return JsonResponse({'process': 'success', 'msg': 'Student details successfully updated!'})
            except Exception as err:
                return JsonResponse({'process': 'failed', 'msg': f'{err}'})

    student = Student.objects.get(pk=pk)

    context_dict = {
        'student': student,
        'classes_list': request.user.teacher.college_classes.all(),
    }
    return render(request, template_name='college/teacher/teacher_update_student.html', context=context_dict)


@login_required
@allowed_users(allowed_roles=['teacher'])
def view_student_lists(request):
    students_info = {}
    college_classes = request.user.teacher.college_classes.all()

    for college_class in college_classes:
        students_info[college_class] = [student for student in Student.objects.all() if
                                        student.college_class == college_class]

    context_dict = {
        'students_info': students_info,
    }
    return render(request, template_name='college/teacher/view_students_list.html', context=context_dict)


@login_required
@allowed_users(allowed_roles=['teacher'])
def college_teacher_classroom(request, pk=None):
    try:
        college_class = CollegeClass.objects.get(pk=pk)
    except Exception as err:
        context_dict = {
            'college_class': None,
        }
        return render(request, template_name='college/teacher/classroom/teacher_classroom.html', context=context_dict)

    try:
        subjects = [subject for subject in Subject.objects.all() if subject in college_class.subjects.all()]
        students = [student for student in Student.objects.all() if student.college_class == college_class]
    except Exception as err:
        context_dict = {
            'college_class': None,
        }
        return render(request, template_name='college/teacher/classroom/teacher_classroom.html', context=context_dict)

    posts = [post for post in ClassWorkPost.objects.all() if post.college_class == college_class]
    textposts = [textpost for textpost in TextPost.objects.all() if textpost.post.college_class == college_class]
    videoposts = [videopost for videopost in VideoPost.objects.all() if videopost.post.college_class == college_class]
    documentposts = [documentpost for documentpost in DocumentPost.objects.all() if
                     documentpost.post.college_class == college_class]
    imageposts = [imagepost for imagepost in ImagePost.objects.all() if imagepost.post.college_class == college_class]
    youtubeposts = [youtubepost for youtubepost in YouTubePost.objects.all() if
                    youtubepost.post.college_class == college_class]
    articleposts = [articlepost for articlepost in ArticlePost.objects.all() if
                    articlepost.post.college_class == college_class]
    classtestposts = [classtestpost for classtestpost in ClassTestPost.objects.all() if
                      classtestpost.post.college_class == college_class]

    posts_display = []

    for post in posts:
        for textpost in textposts:
            if textpost.post == post:
                posts_display.insert(0, textpost)
        for videopost in videoposts:
            if videopost.post == post:
                posts_display.insert(0, videopost)
        for documentpost in documentposts:
            if documentpost.post == post:
                posts_display.insert(0, documentpost)
        for imagepost in imageposts:
            if imagepost.post == post:
                posts_display.insert(0, imagepost)
        for youtubepost in youtubeposts:
            if youtubepost.post == post:
                posts_display.insert(0, youtubepost)
        for articlepost in articleposts:
            if articlepost.post == post:
                posts_display.insert(0, articlepost)
        for classtestpost in classtestposts:
            if classtestpost.post == post:
                posts_display.insert(0, classtestpost)

    comments_and_replies = []

    for comment in PostComment.objects.all():
        for post in posts_display:
            if comment.post == post.post:
                try:
                    replies = CommentReply.objects.filter(postcomment=comment)
                    comments_and_replies.append({
                        'comments': {
                            'post_pk': post.post.pk,
                            'comment': comment,
                            'replies': replies,
                        }
                    })
                except Exception as err:
                    pass

    context_dict = {
        'college_class': college_class,
        'subjects': subjects,
        'students': students,
        'posts_display': posts_display,
        'comments_and_replies': comments_and_replies,
    }

    return render(request, template_name='college/teacher/classroom/teacher_classroom.html', context=context_dict)


@login_required
@allowed_users(allowed_roles=['teacher'])
def college_teacher_classroom_add_post(request, pk=None):
    if request.method == 'POST':
        college = College.objects.get(pk=request.user.teacher.college.pk)
        college_class_pk = pk
        try:
            # Get the data from the form
            title = request.POST.get('title')
            subject_pk = request.POST.get('subject')
            student_pks = request.POST.get('students').split(' ')
            postype = request.POST.get('postype')

            college_class = CollegeClass.objects.get(pk=college_class_pk)

            if postype == 'regular' or postype == 'assignment':
                is_assignment = False
                is_classtest = False
                if postype == 'assignment':
                    is_assignment = True

                classworkpost = ClassWorkPost.objects.create(
                    college_class=college_class,
                    subject=Subject.objects.get(pk=subject_pk),
                    teacher=request.user.teacher,
                    title=title,
                    is_assignment=is_assignment,
                    is_classtest=is_classtest,
                )

                # link students to this post
                this_class_students = [student for student in Student.objects.all() if
                                       student.college_class == college_class]

                if student_pks[0] == 'all':
                    for student in this_class_students:
                        classworkpost.students.add(student)
                else:
                    for student in this_class_students:
                        if str(student.pk) in student_pks:
                            classworkpost.students.add(student)

                post_category = request.POST.get('postcategory')

                if post_category == 'textpost':
                    textpostbody = request.POST.get('textpostbody')
                    TextPost.objects.create(
                        post=classworkpost,
                        body=textpostbody
                    )
                elif post_category == 'videopost':
                    videopostbody = request.POST.get('videopostbody')
                    videopostfile = request.FILES['videopostfile']
                    video_post = VideoPost.objects.create(
                        post=classworkpost,
                        body=videopostbody,
                    )
                    if not video_post.uploadable(file_tobe_uploaded=videopostfile):
                        video_post.delete()
                        classworkpost.delete()
                        err = 'Your college has passed its total upload space limit. ' \
                              'You can no longer upload any files. ' \
                              'Please contact your college administrator regarding this'
                        messages.error(request, f'{err}')
                        return redirect(college_teacher_classroom, pk=college_class_pk)
                    video_post.video_url = videopostfile
                    video_post.save()
                    college.used_storage_space = college.used_storage_space + (
                            decimal.Decimal(video_post.video_url.size) / (1024 * 1024 * 1024))
                    college.save()
                elif post_category == 'documentpost':
                    documentpostbody = request.POST.get('documentpostbody')
                    documentpostfile = request.FILES['documentpostfile']
                    document_post = DocumentPost.objects.create(
                        post=classworkpost,
                        body=documentpostbody,
                    )
                    if not document_post.uploadable(file_tobe_uploaded=documentpostfile):
                        document_post.delete()
                        classworkpost.delete()
                        err = 'Your college has passed its total upload space limit. ' \
                              'You can no longer upload any files. ' \
                              'Please contact your college administrator regarding this'
                        messages.error(request, f'{err}')
                        return redirect(college_teacher_classroom, pk=college_class_pk)
                    document_post.document_url = documentpostfile
                    document_post.save()
                    college.used_storage_space = college.used_storage_space + (
                            decimal.Decimal(document_post.document_url.size) / (1024 * 1024 * 1024))
                    college.save()
                elif post_category == 'imagepost':
                    imagepostbody = request.POST.get('imagepostbody')
                    imagepostfile = request.FILES['imagepostfile']
                    image_post = ImagePost.objects.create(
                        post=classworkpost,
                        body=imagepostbody,
                    )
                    if not image_post.uploadable(file_tobe_uploaded=imagepostfile):
                        image_post.delete()
                        classworkpost.delete()
                        err = 'Your college has passed its total upload space limit. ' \
                              'You can no longer upload any files. ' \
                              'Please contact your college administrator regarding this'
                        messages.error(request, f'{err}')
                        return redirect(college_teacher_classroom, pk=college_class_pk)
                    image_post.image_url = imagepostfile
                    image_post.save()
                    college.used_storage_space = college.used_storage_space + (
                            decimal.Decimal(image_post.image_url.size) / (1024 * 1024 * 1024))
                    college.save()
                elif post_category == 'youtubepost':
                    youtube_link = request.POST.get('youtubepostbody')
                    if youtube_link.count('watch?v=') != 0:
                        youtube_link = youtube_link.replace('watch?v=', 'embed/')
                    YouTubePost.objects.create(
                        post=classworkpost,
                        youtube_link=youtube_link
                    )
                elif post_category == 'articlepost':
                    article_link = request.POST.get('articlepostbody')
                    ArticlePost.objects.create(
                        post=classworkpost,
                        article_link=article_link
                    )

            elif postype == 'classtest':
                is_assignment = False
                is_classtest = True

                classworkpost = ClassWorkPost.objects.create(
                    college_class=college_class,
                    subject=Subject.objects.get(pk=subject_pk),
                    teacher=request.user.teacher,
                    title=title,
                    is_assignment=is_assignment,
                    is_classtest=is_classtest,
                )

                # link students to this post
                this_class_students = [student for student in Student.objects.all() if
                                       student.college_class == college_class]

                if student_pks[0] == 'all':
                    for student in this_class_students:
                        classworkpost.students.add(student)
                else:
                    for student in this_class_students:
                        if str(student.pk) in student_pks:
                            classworkpost.students.add(student)

                classtestpostbody = request.POST.get('classtestpostbody')

                classtestpost = ClassTestPost.objects.create(
                    post=classworkpost,
                    body=classtestpostbody
                )

                totalnoofquestions = int(request.POST.get('totalnoofquestions'))

                for i in range(1, (totalnoofquestions + 1)):
                    question = request.POST.get(f'q{i}')

                    question = Question.objects.create(
                        class_test_post=classtestpost,
                        question=question
                    )

                    option1 = request.POST.get(f'q{i}o1')
                    option2 = request.POST.get(f'q{i}o2')
                    option3 = request.POST.get(f'q{i}o3')
                    option4 = request.POST.get(f'q{i}o4')

                    correct_ans = {
                        f'q{i}o1': option1,
                        f'q{i}o2': option2,
                        f'q{i}o3': option3,
                        f'q{i}o4': option4
                    }

                    correct_option = correct_ans[request.POST.get(f'ans{i}')]

                    Choice.objects.create(
                        question=question,
                        choice=option1,
                        is_correct=(True if correct_option == option1 else False)
                    )

                    Choice.objects.create(
                        question=question,
                        choice=option2,
                        is_correct=(True if correct_option == option2 else False)
                    )

                    if option3 is not None:
                        Choice.objects.create(
                            question=question,
                            choice=option3,
                            is_correct=(True if correct_option == option3 else False)
                        )

                    if option4 is not None:
                        Choice.objects.create(
                            question=question,
                            choice=option4,
                            is_correct=(True if correct_option == option4 else False)
                        )
            return redirect(college_teacher_classroom, pk=college_class_pk)
        except Exception as err:
            messages.error(request, f'{err}')
            return redirect(college_teacher_classroom, pk=college_class_pk)


@login_required
@allowed_users(allowed_roles=['teacher'])
def college_teacher_classroom_view_test(request, pk=None):
    classtestpost = ClassTestPost.objects.get(pk=pk)
    questions = [question for question in Question.objects.all() if question.class_test_post == classtestpost]
    choices = [choice for choice in Choice.objects.all() if choice.question in questions]

    context_dict = {
        'classtestpost': classtestpost,
        'questions': questions,
        'choices': choices,
    }
    return render(request, template_name='college/teacher/classroom/teacher_view_test.html', context=context_dict)


@login_required
@allowed_users(allowed_roles=['teacher'])
def view_tests_submissions(request, class_pk=None):
    college_class = CollegeClass.objects.get(pk=class_pk)
    classworkposts = ClassWorkPost.objects.filter(college_class=college_class)
    classtestposts = [post for post in classworkposts if post.is_classtest]
    classtestposts = [post for post in ClassTestPost.objects.all() if post.post in classtestposts]
    classtest_solutions = [post for post in ClassTestSolution.objects.all() if post.classtest in classtestposts]

    context_dict = {
        'classtest_solutions': classtest_solutions,
    }
    return render(request, template_name='college/teacher/classroom/view_tests_submissions.html', context=context_dict)


@login_required
@allowed_users(allowed_roles=['teacher'])
def view_assignments_submissions(request, class_pk=None):
    college_class = CollegeClass.objects.get(pk=class_pk)
    classworkposts = ClassWorkPost.objects.filter(college_class=college_class)
    assignment_posts = [post for post in classworkposts if post.is_assignment]
    assignment_solutions = [post for post in AssignmentSolution.objects.all() if post.post in assignment_posts]

    context_dict = {
        'assignment_solutions': assignment_solutions,
    }
    return render(request, template_name='college/teacher/classroom/view_assignments_submissions.html',
                  context=context_dict)


@login_required
@allowed_users(allowed_roles=['teacher'])
def view_test_performance(request, pk=None):
    classtestsolution = ClassTestSolution.objects.get(pk=pk)
    student_choices = [choice for choice in StudentChoice.objects.all() if
                       choice.classtestsolution == classtestsolution]

    test_items = []

    for choice in student_choices:
        question = choice.question
        choices = Choice.objects.filter(question=question)
        selected_choice = choice.choice
        test_items.append({
            'question': question,
            'choices': choices,
            'selected_choice': selected_choice,
        })

    context_dict = {
        'classtestsolution': classtestsolution,
        'test_items': test_items,
    }
    return render(request, template_name='college/teacher/classroom/view_test_performance.html',
                  context=context_dict)


@login_required
@allowed_users(allowed_roles=['teacher'])
def college_teacher_classroom_delete_test(request, pk=None):
    college = College.objects.get(pk=request.user.teacher.college.pk)
    post = None
    if request.method == 'POST':
        try:
            post = ClassWorkPost.objects.get(pk=pk)
        except Exception as err:
            return JsonResponse({'process': 'failed', 'msg': f'{err}'})

        try:
            videopost = VideoPost.objects.get(post=post)
            if videopost:
                college.used_storage_space = college.used_storage_space - (
                        decimal.Decimal(videopost.video_url.size) / (1024 * 1024 * 1024))
                college.save()
        except Exception as err:
            pass

        try:
            documentpost = DocumentPost.objects.get(post=post)
            if documentpost:
                college.used_storage_space = college.used_storage_space - (
                        decimal.Decimal(documentpost.document_url.size) / (1024 * 1024 * 1024))
                college.save()
        except Exception as err:
            pass

        try:
            imagepost = ImagePost.objects.get(post=post)
            if imagepost:
                college.used_storage_space = college.used_storage_space - (
                        decimal.Decimal(imagepost.image_url.size) / (1024 * 1024 * 1024))
                college.save()
        except Exception as err:
            pass

        post.delete()
        return JsonResponse({'process': 'success', 'msg': 'Post successfully deleted'})

    return JsonResponse({'process': 'failed', 'msg': 'GET not supported by this endpoint'})


@login_required
@allowed_users(allowed_roles=['student'])
def college_student(request):
    college_class = request.user.student.college_class

    try:
        subjects = [subject for subject in Subject.objects.all() if subject in college_class.subjects.all()]
    except Exception as err:
        context_dict = {
            'college_class': None,
        }
        return render(request, template_name='college/student/classroom/student_classroom.html', context=context_dict)

    posts = [post for post in ClassWorkPost.objects.all() if post.college_class == college_class]
    textposts = [textpost for textpost in TextPost.objects.all() if textpost.post.college_class == college_class]
    videoposts = [videopost for videopost in VideoPost.objects.all() if videopost.post.college_class == college_class]
    documentposts = [documentpost for documentpost in DocumentPost.objects.all() if
                     documentpost.post.college_class == college_class]
    imageposts = [imagepost for imagepost in ImagePost.objects.all() if imagepost.post.college_class == college_class]
    youtubeposts = [youtubepost for youtubepost in YouTubePost.objects.all() if
                    youtubepost.post.college_class == college_class]
    articleposts = [articlepost for articlepost in ArticlePost.objects.all() if
                    articlepost.post.college_class == college_class]
    classtestposts = [classtestpost for classtestpost in ClassTestPost.objects.all() if
                      classtestpost.post.college_class == college_class]

    posts_display = []

    # These loops are necessary to maintain the order of the posts (by datetime of post)
    for post in posts:
        for textpost in textposts:
            if textpost.post == post:
                posts_display.insert(0, textpost)
        for videopost in videoposts:
            if videopost.post == post:
                posts_display.insert(0, videopost)
        for documentpost in documentposts:
            if documentpost.post == post:
                posts_display.insert(0, documentpost)
        for imagepost in imageposts:
            if imagepost.post == post:
                posts_display.insert(0, imagepost)
        for youtubepost in youtubeposts:
            if youtubepost.post == post:
                posts_display.insert(0, youtubepost)
        for articlepost in articleposts:
            if articlepost.post == post:
                posts_display.insert(0, articlepost)
        for classtestpost in classtestposts:
            if classtestpost.post == post:
                posts_display.insert(0, classtestpost)

    comments_and_replies = []

    for comment in PostComment.objects.all():
        for post in posts_display:
            if comment.post == post.post:
                try:
                    replies = CommentReply.objects.filter(postcomment=comment)
                    comments_and_replies.append({
                        'comments': {
                            'post_pk': post.post.pk,
                            'comment': comment,
                            'replies': replies,
                        }
                    })
                except Exception as err:
                    pass

    context_dict = {
        'college_class': college_class,
        'subjects': subjects,
        'posts_display': posts_display,
        'comments_and_replies': comments_and_replies,
    }

    return render(request, template_name='college/student/classroom/student_classroom.html', context=context_dict)


@login_required
@allowed_users(allowed_roles=['student'])
def college_student_assignments(request):
    college_class = request.user.student.college_class

    try:
        subjects = [subject for subject in Subject.objects.all() if subject in college_class.subjects.all()]
    except Exception as err:
        context_dict = {
            'college_class': None,
        }
        return render(request, template_name='college/student/classroom/student_classroom.html', context=context_dict)

    posts = [post for post in ClassWorkPost.objects.all() if
             post.college_class == college_class and post.is_assignment == True]
    textposts = [textpost for textpost in TextPost.objects.all() if textpost.post in posts]
    videoposts = [videopost for videopost in VideoPost.objects.all() if videopost.post in posts]
    documentposts = [documentpost for documentpost in DocumentPost.objects.all() if documentpost.post in posts]
    imageposts = [imagepost for imagepost in ImagePost.objects.all() if imagepost.post in posts]
    youtubeposts = [youtubepost for youtubepost in YouTubePost.objects.all() if youtubepost.post in posts]
    articleposts = [articlepost for articlepost in ArticlePost.objects.all() if articlepost.post in posts]

    posts_display = []

    for post in posts:
        for textpost in textposts:
            if textpost.post == post:
                posts_display.insert(0, textpost)
        for videopost in videoposts:
            if videopost.post == post:
                posts_display.insert(0, videopost)
        for documentpost in documentposts:
            if documentpost.post == post:
                posts_display.insert(0, documentpost)
        for imagepost in imageposts:
            if imagepost.post == post:
                posts_display.insert(0, imagepost)
        for youtubepost in youtubeposts:
            if youtubepost.post == post:
                posts_display.insert(0, youtubepost)
        for articlepost in articleposts:
            if articlepost.post == post:
                posts_display.insert(0, articlepost)

    context_dict = {
        'college_class': college_class,
        'subjects': subjects,
        'posts_display': posts_display,
    }

    return render(request, template_name='college/student/classroom/college_student_assignments.html',
                  context=context_dict)


@login_required
@allowed_users(allowed_roles=['student'])
def college_student_submit_assignment(request, pk=None):
    post = ClassWorkPost.objects.get(pk=pk)
    college = College.objects.get(pk=request.user.student.college.pk)
    assignment_solution = None
    try:
        assignment_solution = AssignmentSolution.objects.get(post=post, student=request.user.student)
    except Exception as err:
        pass

    if request.method == 'POST':
        assignment_solution = AssignmentSolution.objects.create(
            student=request.user.student,
            post=post,
        )
        if assignment_solution.uploadable(file_tobe_uploaded=request.FILES['assignment_file']):
            assignment_solution.file_url = request.FILES['assignment_file']
            assignment_solution.save()
            college.used_storage_space += decimal.Decimal((assignment_solution.file_url.size / (1024 * 1024 * 1024)))
            college.save()
            return redirect(college_student)

        assignment_solution.delete()

        err = 'Your college has passed its total upload space limit. ' \
              'You can no longer upload any files. ' \
              'Please contact your college administrator regarding this'
        messages.error(request, f'{err}')
        return redirect(college_student)

    try:
        textpost = TextPost.objects.get(post=post)
        context_dict = {
            'post': textpost,
            'assignment_solution': assignment_solution,
        }
        return render(request, template_name='college/student/classroom/college_student_submit_assignment.html',
                      context=context_dict)
    except Exception as err:
        pass

    try:
        videopost = VideoPost.objects.get(post=post)
        context_dict = {
            'post': videopost,
            'assignment_solution': assignment_solution,
        }
        return render(request, template_name='college/student/classroom/college_student_submit_assignment.html',
                      context=context_dict)
    except Exception as err:
        pass

    try:
        documentpost = DocumentPost.objects.get(post=post)
        context_dict = {
            'post': documentpost,
            'assignment_solution': assignment_solution,
        }
        return render(request, template_name='college/student/classroom/college_student_submit_assignment.html',
                      context=context_dict)
    except Exception as err:
        pass

    try:
        imagepost = ImagePost.objects.get(post=post)
        context_dict = {
            'post': imagepost,
            'assignment_solution': assignment_solution,
        }
        return render(request, template_name='college/student/classroom/college_student_submit_assignment.html',
                      context=context_dict)
    except Exception as err:
        pass

    try:
        youtubepost = YouTubePost.objects.get(post=post)
        context_dict = {
            'post': youtubepost,
            'assignment_solution': assignment_solution,
        }
        return render(request, template_name='college/student/classroom/college_student_submit_assignment.html',
                      context=context_dict)
    except Exception as err:
        pass

    try:
        articlepost = ArticlePost.objects.get(post=post)
        context_dict = {
            'post': articlepost,
            'assignment_solution': assignment_solution,
        }
        return render(request, template_name='college/student/classroom/college_student_submit_assignment.html',
                      context=context_dict)
    except Exception as err:
        pass

    context_dict = {
        'post': None,
        'assignment_solution': None,
    }
    return render(request, template_name='college/student/classroom/college_student_submit_assignment.html',
                  context=context_dict)


@login_required
@allowed_users(allowed_roles=['student'])
def college_student_reading_materials(request):
    college_class = request.user.student.college_class

    try:
        subjects = [subject for subject in Subject.objects.all() if subject in college_class.subjects.all()]
    except Exception as err:
        context_dict = {
            'college_class': None,
        }
        return render(request, template_name='college/student/classroom/student_classroom.html', context=context_dict)

    posts = [post for post in ClassWorkPost.objects.all() if
             post.college_class == college_class]
    textposts = [textpost for textpost in TextPost.objects.all() if textpost.post in posts]
    documentposts = [documentpost for documentpost in DocumentPost.objects.all() if documentpost.post in posts]

    posts_display = []

    for post in posts:
        for textpost in textposts:
            if textpost.post == post:
                posts_display.insert(0, textpost)
        for documentpost in documentposts:
            if documentpost.post == post:
                posts_display.insert(0, documentpost)

    context_dict = {
        'college_class': college_class,
        'subjects': subjects,
        'posts_display': posts_display,
    }

    return render(request, template_name='college/student/classroom/college_student_reading_materials.html',
                  context=context_dict)


@login_required
@allowed_users(allowed_roles=['student'])
def college_student_videos(request):
    college_class = request.user.student.college_class

    try:
        subjects = [subject for subject in Subject.objects.all() if subject in college_class.subjects.all()]
    except Exception as err:
        context_dict = {
            'college_class': None,
        }
        return render(request, template_name='college/student/classroom/student_classroom.html', context=context_dict)

    posts = [post for post in ClassWorkPost.objects.all() if
             post.college_class == college_class]
    videoposts = [videopost for videopost in VideoPost.objects.all() if videopost.post in posts]
    youtubeposts = [youtubepost for youtubepost in YouTubePost.objects.all() if youtubepost.post in posts]

    posts_display = []

    for post in posts:
        for videopost in videoposts:
            if videopost.post == post:
                posts_display.insert(0, videopost)
        for youtubepost in youtubeposts:
            if youtubepost.post == post:
                posts_display.insert(0, youtubepost)

    context_dict = {
        'college_class': college_class,
        'subjects': subjects,
        'posts_display': posts_display,
    }

    return render(request, template_name='college/student/classroom/college_student_videos.html',
                  context=context_dict)


@login_required
@allowed_users(allowed_roles=['student'])
def college_student_articles(request):
    college_class = request.user.student.college_class

    try:
        subjects = [subject for subject in Subject.objects.all() if subject in college_class.subjects.all()]
    except Exception as err:
        context_dict = {
            'college_class': None,
        }
        return render(request, template_name='college/student/classroom/student_classroom.html', context=context_dict)

    posts = [post for post in ClassWorkPost.objects.all() if
             post.college_class == college_class]
    articleposts = [articlepost for articlepost in ArticlePost.objects.all() if articlepost.post in posts]

    posts_display = []

    for post in posts:
        for articlepost in articleposts:
            if articlepost.post == post:
                posts_display.insert(0, articlepost)

    context_dict = {
        'college_class': college_class,
        'subjects': subjects,
        'posts_display': posts_display,
    }

    return render(request, template_name='college/student/classroom/college_student_articles.html',
                  context=context_dict)


@login_required
@allowed_users(allowed_roles=['student'])
def college_student_classroom_give_test(request, pk=None):
    if request.method == 'POST':
        # This request is for submitting a classtest
        data = json.loads(request.body)
        classtestpost_id = data['classtestpost_id']
        qans = data['qans']

        score = 0
        total_marks = len(qans)

        try:
            classtestpost = ClassTestPost.objects.get(pk=classtestpost_id)

            classtestsolution = ClassTestSolution.objects.create(
                student=request.user.student,
                classtest=classtestpost,
                score=score,
                total_marks=total_marks
            )

            for key, value in qans.items():
                student_choice = StudentChoice.objects.create(
                    classtestsolution=classtestsolution,
                    student=request.user.student,
                    question=Question.objects.get(pk=key),
                    choice=Choice.objects.get(pk=value)
                )

                if student_choice.is_correct:
                    score += 1

                print(student_choice.is_correct)

            classtestsolution.score = score
            classtestsolution.save()

            return JsonResponse({'process': 'success', 'msg': 'Post successfully deleted'})
        except Exception as err:
            return JsonResponse({'process': 'failed', 'msg': f'{err}'})

    classtestpost = ClassTestPost.objects.get(pk=pk)

    questions = [question for question in Question.objects.all() if question.class_test_post == classtestpost]
    choices = [choice for choice in Choice.objects.all() if choice.question in questions]

    context_dict = {
        'classtestpost': classtestpost,
        'questions': questions,
        'choices': choices,
    }

    try:
        classtestsolution = ClassTestSolution.objects.get(
            student=request.user.student,
            classtest=classtestpost,
        )
        context_dict['classtestsolution'] = classtestsolution
    except Exception as err:
        context_dict['classtestsolution'] = None

    return render(request, template_name='college/student/classroom/student_give_test.html', context=context_dict)


@login_required
@allowed_users(allowed_roles=['student', 'teacher'])
def college_teacher_student_account(request):
    return render(request, template_name='college/teacher_student_account.html')


@login_required
@allowed_users(allowed_roles=['student', 'teacher'])
def college_student_classroom_view_post(request, pk=None):
    textpost = TextPost.objects.get(pk=pk)

    context_dict = {
        'textpost': textpost,
    }
    return render(request, template_name='college/classroom_view_post.html', context=context_dict)


@login_required
@allowed_users(allowed_roles=['student', 'teacher'])
def college_classroom_post_comment(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        post_id = data['post_id']
        comment = data['comment']

        try:
            is_teacher = True if request.user.teacher else False
        except Exception as err:
            is_teacher = False

        try:
            classworkpost = ClassWorkPost.objects.get(pk=post_id)
            postcomment = PostComment.objects.create(
                post=classworkpost,
                comment=comment,
                author=request.user,
                is_teacher=is_teacher
            )
        except Exception as err:
            return JsonResponse({
                'process': 'failed',
                'msg': f'{err}'
            })

        return JsonResponse({
            'process': 'success',
            'comment_id': postcomment.pk,
            'author': f'{postcomment.author.first_name} {postcomment.author.last_name}',
            'comment': f'{postcomment.comment}',
            'is_teacher': f'{postcomment.is_teacher}',
            'date': f'{postcomment.date}',
            'msg': 'Comment successfully posted'
        })

    return JsonResponse({
        'process': 'failed',
        'msg': 'GET method not supported'
    })


@login_required
@allowed_users(allowed_roles=['student', 'teacher'])
def college_classroom_post_reply(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        comment_id = data['comment_id']
        replied_to = data['replied_to']

        # This escaping is must because it is marked safe in templates for <b>reply_to_username</b> to display
        # without escaping.
        comment = escape(data["comment"])
        comment = f'{replied_to} {comment}'

        try:
            is_teacher = True if request.user.teacher else False
        except Exception as err:
            is_teacher = False

        try:
            postcomment = PostComment.objects.get(pk=comment_id)
            commentreply = CommentReply.objects.create(
                postcomment=postcomment,
                comment=comment,
                author=request.user,
                is_teacher=is_teacher
            )
        except Exception as err:
            return JsonResponse({
                'process': 'failed',
                'msg': f'{err}'
            })

        return JsonResponse({
            'process': 'success',
            'comment_id': commentreply.postcomment.pk,
            'author': f'{commentreply.author.first_name} {commentreply.author.last_name}',
            'comment': f'{commentreply.comment}',
            'is_teacher': f'{commentreply.is_teacher}',
            'date': f'{commentreply.date}',
            'msg': 'Reply successfully posted'
        })

    return JsonResponse({
        'process': 'failed',
        'msg': 'GET method not supported'
    })


@login_required
@allowed_users(allowed_roles=['student', 'teacher'])
def delete_comment_or_reply(request, pk=None):
    if request.method == 'POST':
        data = json.loads(request.body)
        comment_id = data['comment_id']
        reply_id = data['reply_id']

        if reply_id is None:
            # This request is for deleting a comment
            try:
                comment = PostComment.objects.get(pk=comment_id)
                comment.marked_as_deleted = True
                comment.save()
                return JsonResponse({
                    'process': 'success',
                    'msg': 'Comment deleted successfully'
                })
            except Exception as err:
                return JsonResponse({
                    'process': 'failed',
                    'msg': f'{err}'
                })
        else:
            # This request is for deleting a reply
            try:
                reply = CommentReply.objects.get(pk=reply_id)
                reply.marked_as_deleted = True
                reply.save()
                return JsonResponse({
                    'process': 'success',
                    'msg': 'Reply deleted successfully'
                })
            except Exception as err:
                return JsonResponse({
                    'process': 'failed',
                    'msg': f'{err}'
                })

    return JsonResponse({
        'process': 'failed',
        'msg': 'GET method not supported'
    })


def payment_failed(request):
    return render(request, template_name='payment_failed.html')
