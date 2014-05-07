from django.shortcuts import render
from django.http import HttpResponseRedirect
from boxes.models import Box

def box(request, box_pk):
    return render(request,'box/home.html')

def home(request):
    if request.method == 'POST':
        box = Box(name=request.POST.get('name'))
        box.save()
        return HttpResponseRedirect(box.url())
    return render(request,'home.html')
