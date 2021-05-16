import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.db import IntegrityError
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect

from ..decorators import allowed_users
from ..models import *

from .auth_views import *
from .sybadmin_views import *
from .teacher_views import *
from .student_views import *
from .teach_stud_commonviews import *


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
            teacher.user.delete()
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
                college.user.delete()
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
