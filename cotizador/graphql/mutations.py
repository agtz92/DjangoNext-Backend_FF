import graphene
from .types import ProductType, OrderType, OrderItemType, CustomerType, CompanyType
from cotizador.models import Product, Order, OrderItem, Customer, Company
from django.db import IntegrityError

class CreateProduct(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        description = graphene.String()
        sku = graphene.String(required=True)
        base_price = graphene.Decimal(required=True)

    product = graphene.Field(ProductType)

    @classmethod
    def mutate(cls, root, info, name, sku, base_price, description=None):
        product = Product.objects.create(
            name=name,
            description=description,
            sku=sku,
            base_price=base_price,
        )
        return CreateProduct(product=product)

class UpdateProduct(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        name = graphene.String()
        description = graphene.String()
        sku = graphene.String()
        base_price = graphene.Decimal()

    product = graphene.Field(ProductType)

    @classmethod
    def mutate(cls, root, info, id, **kwargs):
        try:
            product = Product.objects.get(pk=id)
            for key, value in kwargs.items():
                if value is not None:
                    setattr(product, key, value)
            product.save()
            return UpdateProduct(product=product)
        except Product.DoesNotExist:
            raise Exception("Product not found")
class DeleteProduct(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    success = graphene.Boolean()

    @classmethod
    def mutate(cls, root, info, id):
        try:
            product = Product.objects.get(pk=id)
            product.delete()
            return DeleteProduct(success=True)
        except Product.DoesNotExist:
            raise Exception("Product not found")
class OrderItemInput(graphene.InputObjectType):
    product = graphene.ID(required=True)
    quantity = graphene.Int(required=True)
    price = graphene.Decimal(required=True)


class CreateOrder(graphene.Mutation):
    class Arguments:
        customer_id = graphene.ID(required=True)
        items = graphene.List(OrderItemInput, required=True)

    success = graphene.Boolean()
    order = graphene.Field(OrderType)

    @classmethod
    def mutate(cls, root, info, customer_id, items):
        try:
            # Fetch customer
            customer = Customer.objects.get(pk=customer_id)

            # Create the order
            order = Order.objects.create(customer=customer)

            # Create the order items
            order_items = []
            for item in items:
                try:
                    product = Product.objects.get(pk=item.product)
                    order_item = OrderItem(
                        order=order,
                        product=product,
                        quantity=item.quantity,
                        price=item.price,
                    )
                    order_items.append(order_item)
                except Product.DoesNotExist:
                    raise Exception(f"Product with ID {item.product} does not exist")

            OrderItem.objects.bulk_create(order_items)

            return CreateOrder(success=True, order=order)

        except Customer.DoesNotExist:
            raise Exception("Customer not found")
        
class DeleteOrder(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)  # ID of the order to be deleted

    success = graphene.Boolean()
    message = graphene.String()

    @classmethod
    def mutate(cls, root, info, id):
        try:
            # Fetch the order
            order = Order.objects.get(pk=id)
            
            # Delete the order
            order.delete()
            
            return DeleteOrder(success=True, message="Order deleted successfully.")
        except Order.DoesNotExist:
            raise Exception("Order not found")

class DuplicateOrder(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)  # ID of the order to be duplicated

    success = graphene.Boolean()
    new_order = graphene.Field(OrderType)

    @classmethod
    def mutate(cls, root, info, id):
        try:
            # Fetch the original order
            original_order = Order.objects.get(pk=id)

            # Duplicate the order
            new_order = Order.objects.create(customer=original_order.customer)

            # Duplicate the items associated with the order
            new_order_items = []
            for item in original_order.items.all():
                new_order_items.append(
                    OrderItem(
                        order=new_order,
                        product=item.product,
                        quantity=item.quantity,
                        price=item.price,
                    )
                )
            OrderItem.objects.bulk_create(new_order_items)

            return DuplicateOrder(success=True, new_order=new_order)

        except Order.DoesNotExist:
            raise Exception("Order not found")

class UpdateOrder(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)  # ID of the order to be updated
        customer_id = graphene.ID()  # New customer ID (optional)
        items = graphene.List(OrderItemInput)  # Updated order items (optional)

    success = graphene.Boolean()
    message = graphene.String()
    updated_order = graphene.Field(OrderType)

    @classmethod
    def mutate(cls, root, info, id, customer_id=None, items=None):
        try:
            # Fetch the order to be updated
            order = Order.objects.get(pk=id)

            # Update the customer if a new customer ID is provided
            if customer_id:
                try:
                    customer = Customer.objects.get(pk=customer_id)
                    order.customer = customer
                except Customer.DoesNotExist:
                    raise Exception(f"Customer with ID {customer_id} does not exist")

            order.save()

            # Update the items if provided
            if items:
                # Clear existing items and replace them with new ones
                order.items.all().delete()
                new_items = []
                for item in items:
                    try:
                        product = Product.objects.get(pk=item.product)
                        new_items.append(
                            OrderItem(
                                order=order,
                                product=product,
                                quantity=item.quantity,
                                price=item.price,
                            )
                        )
                    except Product.DoesNotExist:
                        raise Exception(f"Product with ID {item.product} does not exist")

                OrderItem.objects.bulk_create(new_items)

            return UpdateOrder(
                success=True,
                message="Order updated successfully.",
                updated_order=order,
            )

        except Order.DoesNotExist:
            raise Exception("Order not found")

class CreateCustomer(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        email = graphene.String(required=True)
        phone = graphene.String(required=False)
        company_id = graphene.ID(required=False)  # Associate with a company (optional)

    customer = graphene.Field(CustomerType)
    success = graphene.Boolean()
    message = graphene.String()

    @classmethod
    def mutate(cls, root, info, name, email, phone=None, company_id=None):
        try:
            # Check if the company exists (if provided)
            company = None
            if company_id:
                try:
                    company = Company.objects.get(pk=company_id)
                except Company.DoesNotExist:
                    return CreateCustomer(
                        success=False,
                        message=f"Company with ID {company_id} does not exist.",
                        customer=None,
                    )

            # Create the customer
            customer = Customer.objects.create(
                name=name,
                email=email,
                phone=phone,
                company=company,
            )
            return CreateCustomer(
                success=True,
                message="Customer created successfully.",
                customer=customer,
            )
        except IntegrityError:
            return CreateCustomer(
                success=False,
                message=f"A customer with the email '{email}' already exists.",
                customer=None,
            )
        except Exception as e:
            return CreateCustomer(
                success=False,
                message=f"An unexpected error occurred: {str(e)}",
                customer=None,
            )
        
class CreateCompany(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        business_line = graphene.String(required=True)
        state = graphene.String(required=True)

    company = graphene.Field(CompanyType)
    success = graphene.Boolean()
    message = graphene.String()

    @classmethod
    def mutate(cls, root, info, name, business_line, state):
        try:
            company = Company.objects.create(
                name=name,
                business_line=business_line,
                state=state,
            )
            return CreateCompany(
                success=True,
                message="Company created successfully.",
                company=company,
            )
        except IntegrityError:
            return CreateCompany(
                success=False,
                message=f"A company with the name '{name}' already exists.",
                company=None,  # Explicitly set company to None
            )
        except Exception as e:
            # Handle other exceptions
            return CreateCompany(
                success=False,
                message=f"An unexpected error occurred: {str(e)}",
                company=None,  # Explicitly set company to None
            )
        
    

class Mutation(graphene.ObjectType):
    create_company = CreateCompany.Field()
    create_customer = CreateCustomer.Field()
    create_product = CreateProduct.Field()
    update_product = UpdateProduct.Field()
    delete_product = DeleteProduct.Field()
    create_order = CreateOrder.Field()
    delete_order = DeleteOrder.Field()
    duplicate_order = DuplicateOrder.Field()
    update_order = UpdateOrder.Field()




