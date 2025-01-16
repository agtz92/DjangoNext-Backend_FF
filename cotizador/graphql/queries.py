import graphene
from cotizador.models import (
    Company, Product, Customer, CustomerTier, CustomerSpecificPrice, Order, OrderItem
)
from .types import (
    CompanyType, ProductType, CustomerType, CustomerTierType,
    CustomerSpecificPriceType, OrderType, OrderItemType
)

class Query(graphene.ObjectType):
    companies = graphene.List(CompanyType)
    company = graphene.Field(CompanyType, id=graphene.ID(required=True))
    products = graphene.List(ProductType)
    product = graphene.Field(ProductType, sku=graphene.String(required=True))
    customers = graphene.List(CustomerType)
    customer = graphene.Field(CustomerType, id=graphene.ID(required=True))  # Query for single customer
    customer_tiers = graphene.List(CustomerTierType)
    customer_specific_prices = graphene.List(CustomerSpecificPriceType)
    orders = graphene.List(OrderType)
    order = graphene.Field(OrderType, id=graphene.ID(required=True))  # Query for single order
    order_items = graphene.List(OrderItemType)

    def resolve_companies(self, info):
        return Company.objects.all()
    
    def resolve_company(self, info, id):
        print(f"Resolving company with ID: {id} (type: {type(id)})")
        try:
            return Company.objects.get(pk=id)
        except Company.DoesNotExist:
            return None

    def resolve_products(self, info):
        return Product.objects.all()

    def resolve_product(self, info, sku):
        try:
            return Product.objects.get(sku=sku)
        except Product.DoesNotExist:
            return None

    def resolve_customers(self, info):
        return Customer.objects.all()

    def resolve_customer(self, info, id):
        try:
            return Customer.objects.get(id=id)
        except Customer.DoesNotExist:
            return None

    def resolve_customer_tiers(self, info):
        return CustomerTier.objects.all()

    def resolve_customer_specific_prices(self, info):
        return CustomerSpecificPrice.objects.all()

    def resolve_orders(self, info):
        return Order.objects.all()

    def resolve_order(self, info, id):
        try:
            return Order.objects.get(id=id)
        except Order.DoesNotExist:
            return None

    def resolve_order_items(self, info):
        return OrderItem.objects.all()
