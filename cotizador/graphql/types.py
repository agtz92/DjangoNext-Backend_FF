import strawberry
from strawberry_django import type as strawberry_django_type
from cotizador.models import (
    Company, Product, Customer, CustomerTier, CustomerSpecificPrice, Order, OrderItem
)


@strawberry_django_type(Company)
class CompanyType:
    id: strawberry.ID
    name: str
    business_line: str
    state: str
    created_at: str
    updated_at: str
    # unnecessary customers: list["CustomerType"] = strawberry.field()

    @strawberry.field
    def customers(self) -> list["CustomerType"]:
        return self.customers.all()


@strawberry_django_type(Customer)
class CustomerType:
    id: strawberry.ID
    name: str
    email: str
    phone: str | None
    company: CompanyType | None
    orders: list["OrderType"] = strawberry.field()

    @strawberry.field
    def resolve_orders(self) -> list["OrderType"]:
        return self.orders.all()


@strawberry_django_type(Order)
class OrderType:
    id: strawberry.ID
    customer: CustomerType
    created_at: str
    updated_at: str
    items: list["OrderItemType"] = strawberry.field()
    total_price: float = strawberry.field()

    @strawberry.field
    def resolve_total_price(self) -> float:
        return self.get_total_price()


@strawberry_django_type(Product)
class ProductType:
    id: strawberry.ID
    name: str
    description: str | None
    sku: str
    base_price: float
    created_at: str
    updated_at: str


@strawberry_django_type(CustomerTier)
class CustomerTierType:
    id: strawberry.ID
    name: str
    discount_percentage: float
    created_at: str
    updated_at: str


@strawberry_django_type(CustomerSpecificPrice)
class CustomerSpecificPriceType:
    id: strawberry.ID
    customer: CustomerType
    product: ProductType
    custom_price: float
    created_at: str
    updated_at: str


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
        return self.get_total_price()
