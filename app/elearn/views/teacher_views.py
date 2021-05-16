import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.db import IntegrityError
from django.http import JsonResponse
from django.shortcuts import render, redirect

from ..decorators import allowed_users
from ..models import *

from .auth_views import *
from .sybadmin_views import *
from .college_views import *
from .student_views import *


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
                student.user.delete()
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
