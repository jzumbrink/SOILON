from django.shortcuts import render

def start(request):
    return render(request, 'soilon/simple_start.html')
