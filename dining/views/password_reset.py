from django.contrib.auth import views


class CustomReset(views.PasswordResetView):
    template_name = 'dining/templates/reset_password.html'
    subject_template_name = 'dining/templates/email/subject.txt'
    html_email_template_name = 'dining/templates/email/content.html'


class CustomResetDone(views.PasswordResetDoneView):
    template_name = 'dining/templates/password_reset_done.html'


class CustomResetComplete(views.PasswordResetCompleteView):
    template_name = 'dining/templates/password_reset_complete.html'


class CustomResetConfirm(views.PasswordResetConfirmView):
    template_name = 'dining/templates/password_reset_confirm.html'
