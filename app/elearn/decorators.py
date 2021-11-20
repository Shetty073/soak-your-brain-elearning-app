"""
This file contains all the decorator functions used in the views.py file.
"""
from django.http import HttpResponse
from django.shortcuts import redirect



def unauthenticated_user(view_func):
    """
    This decorator is there to prevent an authenticated user from visiting the sign in/sign up page again.
    If any authenticated user tried to visit the signin page then he/she will be redirected to their
    respective home page.
    :param view_func:
    :return:
    """

    def wrapper_func(request, *args, **kwargs):
        if request.user.is_authenticated:
            user_group = request.user.groups.all()[0].name
            redirect_to = {
                'sybadmin': redirect('syb_admin_page'),
                'collegeadmin': redirect('college_page'),
                'teacher': redirect('college_teacher'),
                'student': redirect('college_student'),
            }
            return redirect_to[user_group]
        else:
            return view_func(request, *args, **kwargs)

    return wrapper_func


def allowed_users(allowed_roles=None):
    """
    This decorator function prevents an authenticated user from visiting any page that he is not meant to visit.
    The authorization is done with the help of built-in django groups.
    :param allowed_roles:
    :return:
    """

    if allowed_roles is None:
        allowed_roles = []

    def decorator(view_func):
        def wrapper_func(request, *args, **kwargs):
            flag = True
            group = None
            if request.user.groups.exists():
                group = request.user.groups.all()[0].name

            # Check if user belongs to the required group
            if group in allowed_roles:
                # Check if the college's subscription is active
                if group == 'collegeadmin':
                    if not request.user.college.subscription_active or request.user.college.days_left() < 1:
                        flag = False
                elif group == 'teacher':
                    if not request.user.teacher.college.subscription_active or request.user.teacher.college.days_left() < 1:
                        flag = False
                elif group == 'student':
                    if not request.user.student.college.subscription_active or request.user.student.college.days_left() < 1:
                        flag = False

                if flag:
                    return view_func(request, *args, **kwargs)
                else:
                    return redirect('/college/plan_cancelled')

            else:
                # User does not belong to the required group
                return HttpResponse('You are not authorized to view this page')  # TODO: make a standalone page for this

        return wrapper_func

    return decorator
