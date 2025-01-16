import graphene
from graphene_django.types import DjangoObjectType
from cotizador.models import (
    Company, Product, Customer, CustomerTier, CustomerSpecificPrice, Order, OrderItem
)

class CompanyType(DjangoObjectType):
    customers = graphene.List(lambda: CustomerType) 

    class Meta:
        model = Company
        fields = ("id", "name", "business_line", "state", "created_at", "updated_at")

    def resolve_customers(self, info):
        return self.customers.all()


class CustomerType(DjangoObjectType):
    orders = graphene.List(lambda: OrderType)  # Add related orders

    class Meta:
        model = Customer
        fields = ("id", "name", "email", "phone", "company")  # Include company field

    def resolve_orders(self, info):
        # Return all orders related to this customer
        return self.orders.all()


class OrderType(DjangoObjectType):
    total_price = graphene.Float()  # Add a custom field for total price

    class Meta:
        model = Order
        fields = ("id", "customer", "created_at", "updated_at", "items")

    def resolve_total_price(self, info):
        return self.get_total_price()


class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        fields = ("id", "name", "description", "sku", "base_price", "created_at", "updated_at")


class CustomerTierType(DjangoObjectType):
    class Meta:
        model = CustomerTier
        fields = ("id", "name", "discount_percentage", "created_at", "updated_at")


class CustomerSpecificPriceType(DjangoObjectType):
    class Meta:
        model = CustomerSpecificPrice
        fields = ("id", "customer", "product", "custom_price", "created_at", "updated_at")


class OrderItemType(DjangoObjectType):
    total_price = graphene.Float()  # Add a custom field for total price

    class Meta:
        model = OrderItem
        fields = ("id", "order", "product", "quantity", "price")

    def resolve_total_price(self, info):
        return self.get_total_price()
