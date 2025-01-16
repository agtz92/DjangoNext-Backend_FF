from django.contrib import admin
from .models import (
    Product,
    Customer,
    CustomerTier,
    CustomerSpecificPrice,
    Order,
    OrderItem
)

# Register your models here.

# Product Admin
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'sku', 'base_price', 'created_at', 'updated_at')
    search_fields = ('name', 'sku')
    list_filter = ('created_at', 'updated_at')
    ordering = ('name',)


# Customer Admin
@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'created_at', 'updated_at')
    search_fields = ('name', 'email', 'phone')
    list_filter = ('created_at', 'updated_at')
    ordering = ('name',)


# Customer Tier Admin
@admin.register(CustomerTier)
class CustomerTierAdmin(admin.ModelAdmin):
    list_display = ('name', 'discount_percentage', 'created_at', 'updated_at')
    search_fields = ('name',)
    ordering = ('name',)


# Customer Specific Price Admin
@admin.register(CustomerSpecificPrice)
class CustomerSpecificPriceAdmin(admin.ModelAdmin):
    list_display = ('customer', 'product', 'custom_price', 'created_at', 'updated_at')
    search_fields = ('customer__name', 'product__name')
    list_filter = ('created_at', 'updated_at')
    ordering = ('customer', 'product')


# Order Admin
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'created_at', 'updated_at')
    search_fields = ('customer__name', 'id')
    list_filter = ('created_at', 'updated_at')
    ordering = ('-created_at',)


# Order Item Admin
@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'price')
    search_fields = ('order__id', 'product__name')
    ordering = ('order',)
