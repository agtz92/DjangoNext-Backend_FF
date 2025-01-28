import strawberry
from strawberry.types import Info
from cotizador.models import Product, Order, OrderItem, Customer, Company
from django.db import IntegrityError
from .types import ProductType, OrderType, OrderItemType, CustomerType, CompanyType


@strawberry.input
class OrderItemInput:
    product: strawberry.ID
    quantity: int
    price: float


@strawberry.type
class CreateProductResponse:
    success: bool
    product: ProductType | None = None
    message: str | None = None


@strawberry.type
class Mutation:
    @strawberry.mutation
    def create_product(
        self, info: Info, name: str, sku: str, base_price: float, description: str | None = None
    ) -> CreateProductResponse:
        try:
            product = Product.objects.create(
                name=name, description=description, sku=sku, base_price=base_price
            )
            return CreateProductResponse(success=True, product=product)
        except Exception as e:
            return CreateProductResponse(success=False, message=f"Error: {str(e)}")

    @strawberry.mutation
    def update_product(
        self, info: Info, id: strawberry.ID, name: str | None = None, 
        description: str | None = None, sku: str | None = None, base_price: float | None = None
    ) -> CreateProductResponse:
        try:
            product = Product.objects.get(pk=id)
            if name is not None:
                product.name = name
            if description is not None:
                product.description = description
            if sku is not None:
                product.sku = sku
            if base_price is not None:
                product.base_price = base_price
            product.save()
            return CreateProductResponse(success=True, product=product)
        except Product.DoesNotExist:
            return CreateProductResponse(success=False, message="Product not found")

    @strawberry.mutation
    def delete_product(self, info: Info, id: strawberry.ID) -> bool:
        try:
            product = Product.objects.get(pk=id)
            product.delete()
            return True
        except Product.DoesNotExist:
            return False

    @strawberry.mutation
    def create_order(
        self, info: Info, customer_id: strawberry.ID, items: list[OrderItemInput]
    ) -> OrderType | None:
        try:
            customer = Customer.objects.get(pk=customer_id)
            order = Order.objects.create(customer=customer)

            order_items = [
                OrderItem(
                    order=order,
                    product=Product.objects.get(pk=item.product),
                    quantity=item.quantity,
                    price=item.price,
                )
                for item in items
            ]
            OrderItem.objects.bulk_create(order_items)

            return order
        except Customer.DoesNotExist:
            raise Exception("Customer not found")
        except Product.DoesNotExist as e:
            raise Exception(f"Product not found: {str(e)}")

    @strawberry.mutation
    def delete_order(self, info: Info, id: strawberry.ID) -> bool:
        try:
            order = Order.objects.get(pk=id)
            order.delete()
            return True
        except Order.DoesNotExist:
            return False

    @strawberry.mutation
    def duplicate_order(self, info: Info, id: strawberry.ID) -> OrderType | None:
        try:
            original_order = Order.objects.get(pk=id)
            new_order = Order.objects.create(customer=original_order.customer)
            order_items = [
                OrderItem(
                    order=new_order,
                    product=item.product,
                    quantity=item.quantity,
                    price=item.price,
                )
                for item in original_order.items.all()
            ]
            OrderItem.objects.bulk_create(order_items)
            return new_order
        except Order.DoesNotExist:
            raise Exception("Order not found")

    @strawberry.mutation
    def update_order(
        self, info: Info, id: strawberry.ID, customer_id: strawberry.ID | None = None, 
        items: list[OrderItemInput] | None = None
    ) -> OrderType | None:
        try:
            order = Order.objects.get(pk=id)
            if customer_id:
                customer = Customer.objects.get(pk=customer_id)
                order.customer = customer
            if items:
                order.items.all().delete()
                order_items = [
                    OrderItem(
                        order=order,
                        product=Product.objects.get(pk=item.product),
                        quantity=item.quantity,
                        price=item.price,
                    )
                    for item in items
                ]
                OrderItem.objects.bulk_create(order_items)
            order.save()
            return order
        except Order.DoesNotExist:
            raise Exception("Order not found")
        except Customer.DoesNotExist:
            raise Exception("Customer not found")
        except Product.DoesNotExist as e:
            raise Exception(f"Product not found: {str(e)}")

    @strawberry.mutation
    def create_customer(
        self, info: Info, name: str, email: str, phone: str | None = None, 
        company_id: strawberry.ID | None = None
    ) -> CustomerType | None:
        try:
            company = Company.objects.get(pk=company_id) if company_id else None
            customer = Customer.objects.create(name=name, email=email, phone=phone, company=company)
            return customer
        except Company.DoesNotExist:
            raise Exception("Company not found")
        except IntegrityError:
            raise Exception("A customer with this email already exists.")

    @strawberry.mutation
    def create_company(self, info: Info, name: str, business_line: str, state: str) -> CompanyType | None:
        try:
            return Company.objects.create(name=name, business_line=business_line, state=state)
        except IntegrityError:
            raise Exception("A company with this name already exists.")
