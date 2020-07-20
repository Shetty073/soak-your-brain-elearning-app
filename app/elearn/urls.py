from django.urls import path, include
from .views import *

urlpatterns = [
    path('', home, name='home'),
    path('signup/', sign_up, name='signup'),
    path('signin/', sign_in, name='signin'),
    path('checkout/', checkout_page, name='checkout_page'),
    path('admin/', admin_page, name='admin_page'),
    path('college/', college_page, name='college_page'),
]