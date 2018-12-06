from django.shortcuts import render,redirect


def payment(request):
    return render(request, 'dining/templates/peyment.html')