import uuid

from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from hamrokheti import settings


import uuid
from django.conf import settings
from django.db import models

class Order(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    delivery_partner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
                                         related_name='delivery_orders')
    order_date = models.DateTimeField(auto_now_add=True)
    type = models.CharField(max_length=100, choices=[
        ('self', 'self'),
        ('partner', 'partner')
    ], default='self')
    status = models.CharField(max_length=100, choices=[
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
    ], default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    completed = models.BooleanField(default=False)
    checkout_type = models.CharField(max_length=100, choices=[
        ('cash', 'Cash'),
        ('wallet', 'Wallet')
    ], default='cash')
    transaction_uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    payment_type = models.CharField(max_length=100, choices=[
        ('pending', 'Pending'),
        ('complete', 'Complete')
    ], default='pending')

    def __str__(self):
        return f"Order #{self.id} - {self.customer.username}"


@receiver(post_save, sender=Order)
def update_product_quantity(sender, instance, **kwargs):
    if instance.status == 'completed' or instance.status == "delivered":
        for order_item in instance.order_items.all():
            product = order_item.product
            product.quantity_available -= order_item.quantity_ordered
            product.save()


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE)
    quantity_ordered = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Order Item - {self.product.name} - Quantity: {self.quantity_ordered}"
