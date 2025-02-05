from __future__ import annotations  # Delays evaluation of type annotations (Python 3.7+)
import strawberry
from typing import List
from asgiref.sync import sync_to_async
from strawberry_django import type as strawberry_django_type
from cotizador.models import (
    Company, Product, Customer, CustomerTier, CustomerSpecificPrice, Order, OrderItem
)

# 1. Define CompanyType first because CustomerType directly references it.
@strawberry_django_type(Company)
class CompanyType:
    id: strawberry.ID
    name: str
    business_line: str
    state: str
    created_at: str
    updated_at: str
    # Use a forward reference (string) for CustomerType since it's defined later.
    customers: List["CustomerType"] = strawberry.field()

    @strawberry.field
    async def customers(self) -> List[CustomerType]:
        # This resolver fetches the customers for the company asynchronously.
        return await sync_to_async(list)(self.customers.all())


# 2. Define CustomerType next.
@strawberry_django_type(Customer)
class CustomerType:
    id: strawberry.ID
    name: str
    email: str
    phone: str | None
    # CompanyType is already defined above.
    company: CompanyType | None
    # Use a forward reference for OrderType.
    orders: List["OrderType"] = strawberry.field()

    @strawberry.field
    def resolve_orders(self) -> List["OrderType"]:
        # This resolver fetches the orders for the customer.
        return self.orders.all()


# 3. Define OrderType.
@strawberry_django_type(Order)
class OrderType:
    id: strawberry.ID
    customer: CustomerType
    created_at: str
    updated_at: str
    # Use a forward reference for OrderItemType.
    items: List["OrderItemType"] = strawberry.field()
    total_price: float = strawberry.field()

    @strawberry.field
    def resolve_total_price(self) -> float:
        # Calculate total price using a model method (for example).
        return self.get_total_price()


# 4. Define ProductType.
@strawberry_django_type(Product)
class ProductType:
    id: strawberry.ID
    name: str
    description: str | None
    sku: str
    base_price: float
    created_at: str
    updated_at: str


# 5. Define CustomerTierType.
@strawberry_django_type(CustomerTier)
class CustomerTierType:
    id: strawberry.ID
    name: str
    discount_percentage: float
    created_at: str
    updated_at: str


# 6. Define CustomerSpecificPriceType.
@strawberry_django_type(CustomerSpecificPrice)
class CustomerSpecificPriceType:
    id: strawberry.ID
    customer: CustomerType
    product: ProductType
    custom_price: float
    created_at: str
    updated_at: str


# 7. Define OrderItemType last.
@strawberry_django_type(OrderItem)
class OrderItemType:
    id: strawberry.ID
    order: OrderType
    product: ProductType
    quantity: int
    price: float
    total_price: float = strawberry.field()

    @strawberry.field
    def resolve_total_price(self) -> float:
        # Calculate the total price for this order item.
        return self.get_total_price()
