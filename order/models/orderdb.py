from django.db import models


class OrderFood(models.Model):
    food = models.ForeignKey(to='order.RestaurantMenu', on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0)
    invoice = models.ForeignKey(to='order.Invoice', on_delete=models.CASCADE, default='')

    def __str__(self):
        return self.food


class Invoice(models.Model):
    user = models.ForeignKey(to='order.FoodUser', on_delete=models.CASCADE)
    invoice_number = models.DateTimeField(auto_now=True)
    address = models.CharField(max_length=300, default='0')
    amount = models.IntegerField(default=0)
    is_active = models.BooleanField(default=False)
    is_paid = models.BooleanField(default=False)
    is_sent = models.BooleanField(default=False)


class InvoicePendingPayment(models.Model):
    invoice = models.ForeignKey(to='order.Invoice', on_delete=models.CASCADE)
    discount_code = models.CharField(max_length=20)
    code = models.CharField(max_length=20)
    is_active = models.BooleanField(default=False)
    amount = models.IntegerField()
