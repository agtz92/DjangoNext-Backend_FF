import strawberry
from asgiref.sync import sync_to_async
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
    async def companies(self) -> list[CompanyType]:
        return await sync_to_async(list)(Company.objects.all())  # Fix async context

    @strawberry.field
    async def company(self, id: strawberry.ID) -> CompanyType | None:
        try:
            return await sync_to_async(Company.objects.get)(pk=id)  # Fix async context
        except Company.DoesNotExist:
            return None

    @strawberry.field
    async def products(self) -> list[ProductType]:
        return await sync_to_async(list)(Product.objects.all())

    @strawberry.field
    async def product(self, sku: str) -> ProductType | None:
        try:
            return await sync_to_async(Product.objects.get)(sku=sku)
        except Product.DoesNotExist:
            return None

    @strawberry.field
    async def customers(self) -> list[CustomerType]:
        return await sync_to_async(list)(Customer.objects.all())

    @strawberry.field
    async def customer(self, id: strawberry.ID) -> CustomerType | None:
        try:
            return await sync_to_async(Customer.objects.get)(id=id)
        except Customer.DoesNotExist:
            return None

    @strawberry.field
    async def customer_tiers(self) -> list[CustomerTierType]:
        return await sync_to_async(list)(CustomerTier.objects.all())

    @strawberry.field
    async def customer_specific_prices(self) -> list[CustomerSpecificPriceType]:
        return await sync_to_async(list)(CustomerSpecificPrice.objects.all())

    @strawberry.field
    async def orders(self) -> list[OrderType]:
        return await sync_to_async(list)(Order.objects.all())

    @strawberry.field
    async def order(self, id: strawberry.ID) -> OrderType | None:
        try:
            return await sync_to_async(Order.objects.get)(id=id)
        except Order.DoesNotExist:
            return None

    @strawberry.field
    async def order_items(self) -> list[OrderItemType]:
        return await sync_to_async(list)(OrderItem.objects.all())


schema = strawberry.Schema(query=Query)
