from django.shortcuts import render


# Create your views here.
def home(request):
    context_dict = {}
    return render(request, template_name='home.html', context=context_dict)
