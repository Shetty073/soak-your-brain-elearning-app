import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect

from ..decorators import allowed_users
from ..models import *

from .auth_views import *
from .sybadmin_views import *
from .college_views import *
from .teacher_views import *


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
