import strawberry
from cotizador.models import (
    Company, Product, Customer, CustomerTier, CustomerSpecificPrice, Order, OrderItem
)
from .types import (
    CompanyType, ProductType, CustomerType, CustomerTierType,
    CustomerSpecificPriceType, OrderType, OrderItemType
)

@strawberry.type
class Query:
    @strawberry.field
    def companies(self) -> list[CompanyType]:
        return Company.objects.all()

    @strawberry.field
    def company(self, id: strawberry.ID) -> CompanyType | None:
        try:
            return Company.objects.get(pk=id)
        except Company.DoesNotExist:
            return None

    @strawberry.field
    def products(self) -> list[ProductType]:
        return Product.objects.all()

    @strawberry.field
    def product(self, sku: str) -> ProductType | None:
        try:
            return Product.objects.get(sku=sku)
        except Product.DoesNotExist:
            return None

    @strawberry.field
    def customers(self) -> list[CustomerType]:
        return Customer.objects.all()

    @strawberry.field
    def customer(self, id: strawberry.ID) -> CustomerType | None:
        try:
            return Customer.objects.get(id=id)
        except Customer.DoesNotExist:
            return None

    @strawberry.field
    def customer_tiers(self) -> list[CustomerTierType]:
        return CustomerTier.objects.all()

    @strawberry.field
    def customer_specific_prices(self) -> list[CustomerSpecificPriceType]:
        return CustomerSpecificPrice.objects.all()

    @strawberry.field
    def orders(self) -> list[OrderType]:
        return Order.objects.all()

    @strawberry.field
    def order(self, id: strawberry.ID) -> OrderType | None:
        try:
            return Order.objects.get(id=id)
        except Order.DoesNotExist:
            return None

    @strawberry.field
    def order_items(self) -> list[OrderItemType]:
        return OrderItem.objects.all()

schema = strawberry.Schema(query=Query)
