from django.shortcuts import render
from django.http import HttpResponseForbidden, HttpResponse


def home(request):
    if request.method == "GET":
        return render(request, "dining/templates/index.html")
    else:
        return HttpResponseForbidden()


def contact_us(request):
    if request.method == 'POST':
        print(request.POST)
        subject = request.POST.get('contactSubject')
        message = request.POST.get('contactMessage')
        from_email = request.POST.get('contactEmail')
        if subject and message and from_email:
            # try:
            #     send_mail(subject, message, from_email, ['myjahromi@gmail.com'])
            # except BadHeaderError:
            #     return HttpResponse(status=400, content='{"msg":  "هدری وجود ندارد"}')
            return HttpResponse(status=200)
        else:
            return HttpResponse(status=400, content='{"msg": "تمامی فیلدها را پر کنید"}')
    else:
        return HttpResponseForbidden()