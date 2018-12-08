from django.db import models


class Coins(models.Model):
    user = models.ForeignKey(to='dining.CustomUser', related_name='%(class)s_requests_created',
                             on_delete=models.CASCADE)
    introduced_user = models.ForeignKey(to='dining.CustomUser', related_name='%(class)s_requests_introduced',
                                        on_delete=models.CASCADE)
    active = models.BooleanField(default=False)

    def __str__(self):
        return str(self.user)
