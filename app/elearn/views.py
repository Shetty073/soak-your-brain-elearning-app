import json

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.contrib.messages import get_messages
from django.db import IntegrityError
from django.http import JsonResponse
from django.shortcuts import render, redirect

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
            plan.save()

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
            college.save()

            # now at last the College as Customer
            customer = Customer.objects.create(
                user=new_user,
                plan_subscribed=plan,
                first_name=first_name,
                last_name=last_name,
                college_name=college_name,
                email=email_id,
                phone_no=phone_no,
            )
            customer.save()

            # Now log the user in
            auth_user = authenticate(request, username=email_id, password=password1)
            if auth_user is not None:
                login(request, auth_user)
                # TODO: redirect() is not working after login() for some reason, need to look it up and fix it
                return redirect(college_page)
            else:
                return JsonResponse({'process': 'failed', 'msg': 'User authentication system failed'})
        except IntegrityError:
            return JsonResponse({'process': 'failed', 'msg': 'User already exists'})
        except Exception as err:
            return JsonResponse({'process': 'failed', 'msg': f'{str(err)}'})

    plans = Plan.objects.all().values_list('name', flat=True)
    if plan_subscribed not in plans:
        return render(request, template_name='home.html')
    cost_of_selected_plan = Plan.objects.get(name=plan_subscribed).price_per_year
    context_dict = {'plan_selected': plan_subscribed, 'plan_cost': f'₹{int(cost_of_selected_plan)} / year'}
    return render(request, template_name='sign_up.html', context=context_dict)


@unauthenticated_user
def sign_in(request):
    if request.method == 'POST':
        username = request.POST.get('email')  # username and email are one and the same
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
@allowed_users(allowed_roles=['sybadmin'])
def syb_admin_page(request):
    context_dict = {}
    return render(request, template_name='sybadmin/dashboard/dashboard.html', context=context_dict)


@login_required
@allowed_users(allowed_roles=['collegeadmin'])
def college_page(request):
    teachers = Teacher.objects.filter(college=request.user.college)
    departments = Department.objects.filter(college=request.user.college)
    classes = CollegeClass.objects.filter(college=request.user.college)
    context_dict = {
        'teachers': teachers,
        'departments': departments,
        'classes': classes,
    }
    return render(request, template_name='college/admin/college_admin.html', context=context_dict)


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
                                     'subject_name': subject.name})
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
        students_info[college_class] = [student for student in Student.objects.all() if student.college_class == college_class]

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
    textposts = [textpost for textpost in TextPost.objects.all() if textpost.post in posts]
    videoposts = [videopost for videopost in VideoPost.objects.all() if videopost.post in posts]
    documentposts = [documentpost for documentpost in DocumentPost.objects.all() if documentpost.post in posts]
    imageposts = [imagepost for imagepost in ImagePost.objects.all() if imagepost.post in posts]
    youtubeposts = [youtubepost for youtubepost in YouTubePost.objects.all() if youtubepost.post in posts]
    articleposts = [articlepost for articlepost in ArticlePost.objects.all() if articlepost.post in posts]
    classtestposts = [classtestpost for classtestpost in ClassTestPost.objects.all() if classtestpost.post in posts]

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

    context_dict = {
        'college_class': college_class,
        'subjects': subjects,
        'students': students,
        'posts_display': posts_display,
    }

    return render(request, template_name='college/teacher/classroom/teacher_classroom.html', context=context_dict)


@login_required
@allowed_users(allowed_roles=['teacher'])
def college_teacher_classroom_add_post(request, pk=None):
    if request.method == 'POST':
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
                    VideoPost.objects.create(
                        post=classworkpost,
                        body=videopostbody,
                        video_url=videopostfile
                    )
                elif post_category == 'documentpost':
                    documentpostbody = request.POST.get('documentpostbody')
                    documentpostfile = request.FILES['documentpostfile']
                    DocumentPost.objects.create(
                        post=classworkpost,
                        body=documentpostbody,
                        document_url=documentpostfile
                    )
                elif post_category == 'imagepost':
                    imagepostbody = request.POST.get('imagepostbody')
                    imagepostfile = request.FILES['imagepostfile']
                    ImagePost.objects.create(
                        post=classworkpost,
                        body=imagepostbody,
                        image_url=imagepostfile
                    )
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
@allowed_users(allowed_roles=['student'])
def college_student(request):
    context_dict = {}
    return render(request, template_name='college/student/student.html', context=context_dict)


def payment_failed(request):
    return render(request, template_name='payment_failed.html')
