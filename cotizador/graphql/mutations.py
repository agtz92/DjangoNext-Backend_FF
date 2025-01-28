import strawberry
from strawberry.types import Info
from asgiref.sync import sync_to_async
from cotizador.models import Product, Order, OrderItem, Customer, Company
from django.db import IntegrityError
from .types import ProductType, OrderType, OrderItemType, CustomerType, CompanyType


@strawberry.input
class OrderItemInput:
    product: strawberry.ID
    quantity: int
    price: float


@strawberry.type
class GenericResponse:
    success: bool
    message: str | None = None


@strawberry.type
class CreateProductResponse:
    success: bool
    product: ProductType | None = None
    message: str | None = None


@strawberry.type
class CreateCustomerResponse:
    success: bool
    customer: CustomerType | None = None
    message: str | None = None


@strawberry.type
class CreateOrderResponse:
    success: bool
    order: OrderType | None = None
    message: str | None = None
    order_items: list[OrderItemType] | None = None

    
@strawberry.type
class CreateCompanyResponse:
    success: bool
    company: CompanyType | None = None
    message: str | None = None


@strawberry.type
class Mutation:
    @strawberry.mutation
    async def create_product(
        self, info: Info, name: str, sku: str, base_price: float, description: str | None = None
    ) -> CreateProductResponse:
        try:
            product = await sync_to_async(Product.objects.create)(
                name=name, description=description, sku=sku, base_price=base_price
            )
            return CreateProductResponse(success=True, product=product)
        except Exception as e:
            return CreateProductResponse(success=False, message=f"Error: {str(e)}")

    @strawberry.mutation
    async def update_product(
        self, info: Info, id: strawberry.ID, name: str | None = None, 
        description: str | None = None, sku: str | None = None, base_price: float | None = None
    ) -> CreateProductResponse:
        try:
            product = await sync_to_async(Product.objects.get)(pk=id)
            if name is not None:
                product.name = name
            if description is not None:
                product.description = description
            if sku is not None:
                product.sku = sku
            if base_price is not None:
                product.base_price = base_price
            await sync_to_async(product.save)()
            return CreateProductResponse(success=True, product=product, message="Product updated successfully.")
        except Product.DoesNotExist:
            return CreateProductResponse(success=False, product=None, message="Product not found.")
        except IntegrityError as e:
            return CreateProductResponse(success=False, product=None, message=f"Integrity error: {str(e)}")
        except Exception as e:
            return CreateProductResponse(success=False, product=None, message=f"Error: {str(e)}")


    @strawberry.mutation
    async def delete_product(self, info: Info, id: strawberry.ID) -> GenericResponse:
        try:
            product = await sync_to_async(Product.objects.get)(pk=id)
            await sync_to_async(product.delete)()
            return GenericResponse(success=True, message="Product deleted successfully.")
        except Product.DoesNotExist:
            return GenericResponse(success=False, message="Product not found.")
        except Exception as e:
            return GenericResponse(success=False, message=f"Error: {str(e)}")


    @strawberry.mutation
    async def create_order(
        self, info: Info, customer_id: strawberry.ID, items: list[OrderItemInput]
    ) -> CreateOrderResponse:
        try:
            # Fetch customer
            customer = await sync_to_async(Customer.objects.get)(pk=customer_id)

            # Create the order
            order = await sync_to_async(Order.objects.create)(customer=customer)

            # Create order items
            order_items = []
            for item in items:
                product = await sync_to_async(Product.objects.get)(pk=item.product)
                order_item = OrderItem(
                    order=order,
                    product=product,
                    quantity=item.quantity,
                    price=item.price,
                )
                order_items.append(order_item)

            # Bulk create the order items
            await sync_to_async(OrderItem.objects.bulk_create)(order_items)

            # Retrieve the created items
            created_order_items = await sync_to_async(list)(
                OrderItem.objects.filter(order=order)
            )

            return CreateOrderResponse(
                success=True,
                order=order,
                order_items=created_order_items,
                message="Order created successfully."
            )
        except Customer.DoesNotExist:
            return CreateOrderResponse(
                success=False,
                message="Customer not found.",
                order=None,
                order_items=None
            )
        except Product.DoesNotExist as e:
            return CreateOrderResponse(
                success=False,
                message=f"Product not found: {str(e)}",
                order=None,
                order_items=None
            )
        except Exception as e:
            return CreateOrderResponse(
                success=False,
                message=f"An error occurred: {str(e)}",
                order=None,
                order_items=None
            )


    @strawberry.mutation
    async def delete_order(self, info: Info, id: strawberry.ID) -> GenericResponse:
        try:
            order = await sync_to_async(Order.objects.get)(pk=id)
            await sync_to_async(order.delete)()
            return GenericResponse(success=True, message="Order deleted successfully.")
        except Order.DoesNotExist:
            return GenericResponse(success=False, message="Order not found.")
        except Exception as e:
            return GenericResponse(success=False, message=f"An error occurred: {str(e)}")


    @strawberry.mutation
    async def duplicate_order(
        self, info: Info, id: strawberry.ID
    ) -> CreateOrderResponse:
        try:
            original_order = await sync_to_async(Order.objects.get)(pk=id)

            # Create a new order
            new_order = await sync_to_async(Order.objects.create)(customer=original_order.customer)

            # Duplicate the items
            order_items = [
                OrderItem(
                    order=new_order,
                    product=item.product,
                    quantity=item.quantity,
                    price=item.price,
                )
                for item in await sync_to_async(list)(original_order.items.all())
            ]
            await sync_to_async(OrderItem.objects.bulk_create)(order_items)

            # Retrieve the duplicated items
            duplicated_order_items = await sync_to_async(list)(OrderItem.objects.filter(order=new_order))

            return CreateOrderResponse(
                success=True,
                order=new_order,
                order_items=duplicated_order_items,
                message="Order duplicated successfully."
            )
        except Order.DoesNotExist:
            return CreateOrderResponse(
                success=False,
                message="Order not found.",
                order=None,
                order_items=None
            )
        except Exception as e:
            return CreateOrderResponse(
                success=False,
                message=f"An error occurred: {str(e)}",
                order=None,
                order_items=None
            )


    @strawberry.mutation
    async def update_order(
        self, info: Info, id: strawberry.ID, customer_id: strawberry.ID | None = None, 
        items: list[OrderItemInput] | None = None
    ) -> CreateOrderResponse:
        try:
            order = await sync_to_async(Order.objects.get)(pk=id)

            # Update the customer if provided
            if customer_id:
                customer = await sync_to_async(Customer.objects.get)(pk=customer_id)
                order.customer = customer

            # Update order items if provided
            if items:
                await sync_to_async(order.items.all().delete)()  # Delete existing items
                order_items = [
                    OrderItem(
                        order=order,
                        product=await sync_to_async(Product.objects.get)(pk=item.product),
                        quantity=item.quantity,
                        price=item.price,
                    )
                    for item in items
                ]
                await sync_to_async(OrderItem.objects.bulk_create)(order_items)

            await sync_to_async(order.save)()  # Save the order

            # Retrieve the updated items
            updated_order_items = await sync_to_async(list)(OrderItem.objects.filter(order=order))

            return CreateOrderResponse(
                success=True,
                order=order,
                order_items=updated_order_items,
                message="Order updated successfully."
            )
        except Order.DoesNotExist:
            return CreateOrderResponse(
                success=False,
                message="Order not found.",
                order=None,
                order_items=None
            )
        except Customer.DoesNotExist:
            return CreateOrderResponse(
                success=False,
                message="Customer not found.",
                order=None,
                order_items=None
            )
        except Product.DoesNotExist as e:
            return CreateOrderResponse(
                success=False,
                message=f"Product not found: {str(e)}",
                order=None,
                order_items=None
            )
        except Exception as e:
            return CreateOrderResponse(
                success=False,
                message=f"An error occurred: {str(e)}",
                order=None,
                order_items=None
            )


    @strawberry.mutation
    async def create_customer(
        self, info: Info, name: str, email: str, phone: str | None = None, company_id: strawberry.ID | None = None
    ) -> CreateCustomerResponse:
        try:
            company = await sync_to_async(Company.objects.get)(pk=company_id) if company_id else None
            customer = await sync_to_async(Customer.objects.create)(
                name=name, email=email, phone=phone, company=company
            )
            return CreateCustomerResponse(success=True, customer=customer, message="Customer created successfully.")
        except Company.DoesNotExist:
            return CreateCustomerResponse(success=False, message="Company not found.")
        except IntegrityError:
            return CreateCustomerResponse(success=False, message="A customer with this email already exists.")
        except Exception as e:
            return CreateCustomerResponse(success=False, message=f"Error: {str(e)}")
        
    @strawberry.mutation
    async def update_customer(
        self,
        info: Info,
        id: strawberry.ID,
        name: str | None = None,
        email: str | None = None,
        phone: str | None = None,
        company_id: strawberry.ID | None = None
    ) -> CreateCustomerResponse:
        try:
            # Fetch the customer
            customer = await sync_to_async(Customer.objects.get)(pk=id)

            # Update customer details
            if name is not None:
                customer.name = name
            if email is not None:
                customer.email = email
            if phone is not None:
                customer.phone = phone
            if company_id is not None:
                try:
                    company = await sync_to_async(Company.objects.get)(pk=company_id)
                    customer.company = company
                except Company.DoesNotExist:
                    return CreateCustomerResponse(
                        success=False, customer=None, message="Company not found."
                    )

            # Save the updated customer
            await sync_to_async(customer.save)()

            return CreateCustomerResponse(
                success=True,
                customer=customer,
                message="Customer updated successfully."
            )
        except Customer.DoesNotExist:
            return CreateCustomerResponse(
                success=False, customer=None, message="Customer not found."
            )
        except IntegrityError as e:
            return CreateCustomerResponse(
                success=False, customer=None, message=f"Integrity error: {str(e)}"
            )
        except Exception as e:
            return CreateCustomerResponse(
                success=False, customer=None, message=f"An error occurred: {str(e)}"
            )

    @strawberry.mutation
    async def delete_customer(self, info: Info, id: strawberry.ID) -> GenericResponse:
        try:
            # Fetch the customer
            customer = await sync_to_async(Customer.objects.get)(pk=id)
            await sync_to_async(customer.delete)()  # Delete the customer

            return GenericResponse(success=True, message="Customer deleted successfully.")
        except Customer.DoesNotExist:
            return GenericResponse(success=False, message="Customer not found.")
        except Exception as e:
            return GenericResponse(success=False, message=f"An error occurred: {str(e)}")


    @strawberry.mutation
    async def create_company(
        self, info: Info, name: str, business_line: str, state: str
    ) -> CreateCompanyResponse:
        try:
            company = await sync_to_async(Company.objects.create)(
                name=name, business_line=business_line, state=state
            )
            return CreateCompanyResponse(
                success=True,
                company=company,
                message="Company created successfully."
            )
        except IntegrityError:
            return CreateCompanyResponse(
                success=False,
                message="A company with this name already exists."
            )
        except Exception as e:
            return CreateCompanyResponse(
                success=False,
                message=f"An error occurred: {str(e)}"
            )


    @strawberry.mutation
    async def update_company(
        self,
        info: Info,
        id: strawberry.ID,
        name: str | None = None,
        business_line: str | None = None,
        state: str | None = None
    ) -> CreateCompanyResponse:
        try:
            # Fetch the company
            company = await sync_to_async(Company.objects.get)(pk=id)

            # Update company details
            if name is not None:
                company.name = name
            if business_line is not None:
                company.business_line = business_line
            if state is not None:
                company.state = state

            # Save the updated company
            await sync_to_async(company.save)()

            return CreateCompanyResponse(
                success=True,
                company=company,
                message="Company updated successfully."
            )
        except Company.DoesNotExist:
            return CreateCompanyResponse(
                success=False,
                company=None,
                message="Company not found."
            )
        except IntegrityError as e:
            return CreateCompanyResponse(
                success=False,
                company=None,
                message=f"Integrity error: {str(e)}"
            )
        except Exception as e:
            return CreateCompanyResponse(
                success=False,
                company=None,
                message=f"An error occurred: {str(e)}"
            )

    @strawberry.mutation
    async def delete_company(self, info: Info, id: strawberry.ID) -> GenericResponse:
        try:
            # Fetch the company
            company = await sync_to_async(Company.objects.get)(pk=id)
            await sync_to_async(company.delete)()  # Delete the company

            return GenericResponse(success=True, message="Company deleted successfully.")
        except Company.DoesNotExist:
            return GenericResponse(success=False, message="Company not found.")
        except Exception as e:
            return GenericResponse(success=False, message=f"An error occurred: {str(e)}")
