from django.urls import path, include
from .views import *

urlpatterns = [
    path('', home, name='home'),
    path('signup/', home, name='signup'),
    path('signup/<str:plan_subscribed>', sign_up, name='signup'),
    path('signin/', sign_in, name='signin'),
    path('signout/', sign_out, name='signout'),
    path('checkout/', checkout_page, name='checkout_page'),
    path('sybadmin/', syb_admin_page, name='syb_admin_page'),
    path('college/', college_page, name='college_page'),
    path('college/add_teachers', college_add_teachers, name='college_add_teachers'),
    path('college/add_classes', college_add_classes, name='college_add_classes'),
    path('college/teacher', college_teacher, name='college_teacher'),
    path('college/student', college_student, name='college_student'),
]
