from dining.models import CustomUser

trans = {"۱": "1", "۲": "2", "۳": "3", "۴": "4", "۵": "5", "۶": "6", "۷": "7", "۸": "8", "۹": "9", "۰": "0"}
users = CustomUser.objects.all()
for item in users:
    flag = False
    for number in item.phone:
        if number in trans:
            flag = True
    if flag:
        n = ''
    else:
        n = item.phone
    for number in item.phone:
        na = ''
        if number in trans:
            na = trans[number]
            n = n + na
    item.phone = n
    item.save()
