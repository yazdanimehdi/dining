import telegram

try:
    from urllib.parse import quote_plus  # python 3
except:
    pass

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, redirect
from django.utils import timezone

from order.models import Invoice, OrderFood


def post_list(request):
    today = timezone.now().date()
    invoices = Invoice.objects.filter(is_sent=False, is_active=True)
    queryset_list = []
    for item in invoices:
        queryset_list.append((item, OrderFood.objects.filter(invoice=item)))
    queryset_list.sort(key=lambda a: a[0].active, reverse=True)
    paginator = Paginator(queryset_list, 8)  # Show 25 contacts per page
    page_request_var = "page"
    page = request.GET.get(page_request_var)
    try:
        queryset = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        queryset = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        queryset = paginator.page(paginator.num_pages)

    context = {
        "object_list": queryset,
        "title": "لیست سفارش‌ها",
        "page_request_var": page_request_var,
        "today": today,
    }
    if request.method == 'POST':
        post_id = request.POST.get('id')
        if post_id is not None:
            delivered = Invoice.objects.get(id=post_id)
            delivered.is_sent = True
            delivered.save()

            def send(msg, chat_id, token):
                bot = telegram.Bot(token=token)
                bot.send_message(chat_id=chat_id, text=msg)

            bot_token = '884113858:AAG05koed7NLj6o3n8y5l7YegKa3OOfd36M'
            message = "سفارشت ارسال شد منتظرش باش"
            send(message, delivered.user.chat_id, bot_token)

        return redirect('/order/radbanoo')
    return render(request, "order/templates/order_list.html", context)


def all_list(request):
    today = timezone.now().date()
    invoices = Invoice.objects.filter(is_sent=True, is_active=True)
    queryset_list = []
    for item in invoices:
        queryset_list.append((item, OrderFood.objects.filter(invoice=item)))
    queryset_list.sort(key=lambda a: a[0].id, reverse=True)
    paginator = Paginator(queryset_list, 8)  # Show 25 contacts per page
    page_request_var = "page"
    page = request.GET.get(page_request_var)
    try:
        queryset = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        queryset = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        queryset = paginator.page(paginator.num_pages)

    context = {
        "object_list": queryset,
        "title": "لیست سفارش‌ها",
        "page_request_var": page_request_var,
        "today": today,
    }
    return render(request, "order/templates/order_all.html", context)
