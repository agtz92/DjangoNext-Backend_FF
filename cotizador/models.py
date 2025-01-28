from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid

# Create your models here.
class CustomUser(AbstractUser):

    email = models.EmailField(blank=False, max_length=254, verbose_name="email address")

    USERNAME_FIELD = "username"   # e.g: "username", "email"
    EMAIL_FIELD = "email"         # e.g: "email", "primary_email"

class Company(models.Model):
    id = models.CharField(
        max_length=255, 
        primary_key=True, 
        default=uuid.uuid4,  # Automatically generate a UUID for new instances
        editable=False
    )
    name = models.CharField(max_length=255, unique=True)
    business_line = models.CharField(max_length=255)
    state = models.CharField(max_length=100)  # Text field for country state
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Product(models.Model):
    """
    Represents a product in the system.
    """
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    sku = models.CharField(max_length=100, unique=True, verbose_name="Stock Keeping Unit")
    base_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Base Price")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Customer(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True, blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="customers", null=False, default = "ff02cbc6-f5b1-49c3-b7f2-500252cb0ad8")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class CustomerTier(models.Model):
    """
    Represents a pricing tier that can be associated with a customer.
    """
    name = models.CharField(max_length=100, unique=True)
    discount_percentage = models.DecimalField(
        max_digits=5, decimal_places=2,
        help_text="Percentage discount applied to base price, e.g., 10.00 for 10%."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.discount_percentage}%)"


class CustomerSpecificPrice(models.Model):
    """
    Represents a specific price for a product assigned to a customer.
    """
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="specific_prices")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="specific_prices")
    custom_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Custom Price")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("customer", "product")
        verbose_name = "Customer Specific Price"
        verbose_name_plural = "Customer Specific Prices"

    def __str__(self):
        return f"{self.customer.name} - {self.product.name} @ {self.custom_price}"


class Order(models.Model):
    customer = models.ForeignKey('Customer', on_delete=models.CASCADE, related_name="orders")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_total_price(self):
        total = sum(item.quantity * item.price for item in self.items.all())
        return total

    def __str__(self):
        return f"Order #{self.id} by {self.customer.name}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def get_total_price(self):
        return self.quantity * self.price

    def __str__(self):
        return f"{self.quantity} x {self.product.name} @ {self.price} each"
