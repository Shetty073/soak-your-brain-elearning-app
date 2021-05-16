import json

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.utils.html import escape

from ..decorators import allowed_users
from ..models import *


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
