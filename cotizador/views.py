from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from django.shortcuts import render, get_object_or_404, redirect, HttpResponse
from django.forms import inlineformset_factory
import uuid, json

from .models import Product, Customer, Order, OrderItem, CustomerSpecificPrice, Company
from .serializers import ProductSerializer, CustomerSerializer, OrderSerializer
from .forms import CustomerForm, ProductForm, OrderForm, OrderItemForm, CompanyForm
from rest_framework.exceptions import NotFound



# Product API ViewSet

class ProductViewSet(ModelViewSet):
    """
    A ViewSet for viewing and editing product instances.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    lookup_field = 'sku'  # Use SKU instead of the default ID for lookups

    def retrieve(self, request, *args, **kwargs):
        # Override to fetch by SKU
        sku = kwargs.get(self.lookup_field)  # DRF uses `lookup_field` here
        # print(f"Retrieve called with SKU: {sku}")
        try:
            product = Product.objects.get(sku=sku)
        except Product.DoesNotExist:
            raise NotFound(f"Product with SKU '{sku}' not found.")
        serializer = self.get_serializer(product)
        # print(f"Retrieved Product Data: {serializer.data}")
        return Response(serializer.data)

# Customer API ViewSet
class CustomerViewSet(ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer

# Order API ViewSet
class OrderViewSet(ModelViewSet):
    queryset = Order.objects.prefetch_related('items')  # Optimize queries
    serializer_class = OrderSerializer

def home(request):
    return render(request, "home.html")

# Product Views
def product_list(request):
    products = Product.objects.all()
    return render(request, "products_list.html", {"products": products})


def product_detail(request, sku):
    product = get_object_or_404(Product, sku=sku)
    if request.headers.get('accept') == 'application/json':
        return JsonResponse({
            "sku": product.sku,
            "name": product.name,
            "description": product.description,
            "base_price": str(product.base_price),
        })
    return render(request, "product_detail.html", {"product": product})



# Customer Views
def customer_list(request):
    customers = Customer.objects.select_related('company')  # Optimize query
    return render(request, "customer_list.html", {"customers": customers})



def customer_detail(request, pk):
    customer = get_object_or_404(Customer.objects.select_related('company'), pk=pk)
    return render(request, "customer_detail.html", {"customer": customer})




#order
def order_list(request):
    # Fetch all orders and their associated items and products
    orders = Order.objects.all().select_related('customer').prefetch_related('items__product')  # Optimize the query
    
    order_data = []
    for order in orders:
        # For each order, get its items and product details (name and SKU)
        items = []
        for item in order.items.all():  # use the related name 'items' from the ForeignKey in OrderItem
            items.append({
                'product_name': item.product.name,
                'sku': item.product.sku,
                'quantity': item.quantity,
                'price': item.price,
            })
        order_data.append({
            'id': order.id,
            'customer': order.customer.name,
            'order_items': items
        })

    return render(request, "order_list.html", {"orders": order_data})





def order_detail(request, pk):
    order = get_object_or_404(Order, pk=pk)
    return render(request, "order_detail.html", {"order": order})


# Customer Specific Price Views
def customer_price_list(request):
    customer_prices = CustomerSpecificPrice.objects.all()
    return render(request, "customer_price_list.html", {"customer_prices": customer_prices})

# Customer Price Detail
def customer_price_detail(request, pk):
    customer_price = get_object_or_404(CustomerSpecificPrice, pk=pk)
    return render(request, "customer_price_detail.html", {"customer_price": customer_price})

#Add Customer
def add_customer(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('customer_list')  # Redirect after saving
        else:
            print(form.errors)  # Debug validation errors
    else:
        form = CustomerForm()
    return render(request, 'add_customer.html', {'form': form})


#Add Product
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('product_list')  # Redirect to product list after successful addition
    else:
        form = ProductForm()
    return render(request, 'add_product.html', {'form': form})

# Add Order View Django
def add_order(request):
    OrderItemFormSet = inlineformset_factory(
        Order, 
        OrderItem, 
        form=OrderItemForm, 
        extra=3,  # Allow adding up to 3 items initially
        can_delete=True
    )

    if request.method == 'POST':
        order_form = OrderForm(request.POST)
        item_formset = OrderItemFormSet(request.POST)

        if order_form.is_valid() and item_formset.is_valid():
            order = order_form.save()  # Save the order
            item_formset.instance = order
            item_formset.save()  # Save the associated order items
            return redirect('order_list')

    else:
        order_form = OrderForm()
        item_formset = OrderItemFormSet()

    return render(request, 'add_order.html', {
        'order_form': order_form,
        'item_formset': item_formset,
    })
    
##Create Order Nextjs

@csrf_exempt
def create_order(request):
    if request.method == 'POST':
        try:
            # Parse the incoming JSON payload
            data = json.loads(request.body)

            # Validate and retrieve the customer
            customer_id = data.get("customer")
            if not customer_id:
                return JsonResponse({"error": "Customer is required."}, status=400)
            try:
                customer = Customer.objects.get(id=customer_id)
            except Customer.DoesNotExist:
                return JsonResponse({"error": "Invalid customer ID."}, status=400)

            # Validate order items
            items = data.get("items", [])
            if not items:
                return JsonResponse({"error": "At least one order item is required."}, status=400)

            order_items = []
            for item in items:
                product_id = item.get("product")
                quantity = item.get("quantity")
                price = item.get("price")

                if not product_id or not quantity or not price:
                    return JsonResponse({"error": "Each order item must include product, quantity, and price."}, status=400)

                try:
                    product = Product.objects.get(id=product_id)
                except Product.DoesNotExist:
                    return JsonResponse({"error": f"Invalid product ID: {product_id}"}, status=400)

                # Prepare the OrderItem instance
                order_items.append(OrderItem(
                    product=product,
                    quantity=quantity,
                    price=price
                ))

            # Create the Order
            order = Order.objects.create(customer=customer)

            # Associate order items with the order
            for item in order_items:
                item.order = order

            # Bulk create order items
            OrderItem.objects.bulk_create(order_items)

            # Return a success response
            return JsonResponse({"order_id": order.id}, status=201)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON payload."}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method."}, status=405)




#Update product
def update_product(request, sku):
    product = get_object_or_404(Product, sku=sku)
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            return redirect('product_list')  # Redirect to the product list page
    else:
        form = ProductForm(instance=product)

    return render(request, 'update_product.html', {'form': form, 'product': product})

#Update Customer
def update_customer(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            return redirect('customer_list')  # Redirect after updating
    else:
        form = CustomerForm(instance=customer)
    return render(request, 'update_customer.html', {'form': form, 'customer': customer})


#Update Order
def update_order(request, pk):
    order = get_object_or_404(Order, pk=pk)

    OrderItemFormSet = inlineformset_factory(
        Order, OrderItem, form=OrderItemForm, extra=1, can_delete=True
    )

    if request.method == 'POST':
        order_form = OrderForm(request.POST, instance=order)
        formset = OrderItemFormSet(request.POST, instance=order)

        if order_form.is_valid() and formset.is_valid():
            order = order_form.save()
            formset.save()
            return redirect('order_list')
        else:
            print("Order form errors:", order_form.errors)
            for i, form in enumerate(formset):
                print(f"Formset {i} errors:", form.errors)

    else:
        order_form = OrderForm(instance=order)
        formset = OrderItemFormSet(instance=order)

    return render(request, 'update_order.html', {
        'order_form': order_form,
        'formset': formset,
        'order': order,
    })



#Delete Customer
def delete_customer(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == "POST":
        customer.delete()
        return redirect('customer_list')  # Redirect to the customer list after deletion
    return render(request, 'delete_customer.html', {'customer': customer})

#Delete Product
def delete_product(request, sku):
    product = get_object_or_404(Product, sku=sku)
    if request.method == "POST":
        product.delete()
        return redirect('product_list')  # Redirect to the product list after deletion
    return render(request, 'delete_product.html', {'product': product})

#Delete Order
def delete_order(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if request.method == "POST":
        order.delete()
        return redirect('order_list')  # Redirect to the order list after deletion
    return render(request, 'delete_order.html', {'order': order})

#Duplicate Customer
def duplicate_customer(request, pk):
    original_customer = get_object_or_404(Customer, pk=pk)

    if request.method == "POST":
        try:
            # Duplicate the customer
            new_customer = Customer.objects.create(
                id=str(uuid.uuid4()),  # Ensure a unique ID
                name=f"Copy of {original_customer.name}",
                email=None,  # Avoid conflicts
                phone=original_customer.phone,
            )
            return redirect('update_customer', pk=new_customer.pk)
        except Exception as e:
            # Redirect to the customer list with an error message
            print(f"Error duplicating customer: {e}")
            return redirect('customer_list')  # Redirect to the list page

    return render(request, 'confirm_duplicate_customer.html', {'customer': original_customer})





#Duplicate Product
def duplicate_product(request, sku):
    # Retrieve the original product
    original_product = get_object_or_404(Product, sku=sku)

    if request.method == "POST":
        # Duplicate the product (excluding the primary key)
        new_product = Product.objects.create(
            name=f"Copy of {original_product.name}",
            description=original_product.description,
            sku=f"{original_product.sku}-copy",
            base_price=original_product.base_price,
        )

        # Redirect to the update page for the new product
        return redirect('update_product', sku=new_product.sku)

    return render(request, 'confirm_duplicate_product.html', {'product': original_product})


#Duplicate Order
def duplicate_order(request, pk):
    original_order = get_object_or_404(Order, pk=pk)

    if request.method == "POST":
        # Duplicate the order and its items
        new_order = Order.objects.create(
            customer=original_order.customer,
        )
        for item in original_order.items.all():
            OrderItem.objects.create(
                order=new_order,
                product=item.product,
                quantity=item.quantity,
                price=item.price,
            )
        return redirect('update_order', pk=new_order.pk)

    return render(request, 'confirm_duplicate_order.html', {'order': original_order})


# List all companies
def company_list(request):
    companies = Company.objects.all()
    return render(request, "company_list.html", {"companies": companies})

# Company details
def company_detail(request, pk):
    company = get_object_or_404(Company, pk=pk)
    if request.headers.get('accept') == 'application/json':
        return JsonResponse({
            "id": str(company.id),
            "name": company.name,
            "business_line": company.business_line,
        })
    return render(request, "company_detail.html", {"company": company}) 

# Add a new company
def add_company(request):
    if request.method == 'POST':
        form = CompanyForm(request.POST)
        if form.is_valid():
            form.save()  # Save the company to the database
            return redirect('company_list')  # Redirect to the company list page
        else:
            print(form.errors)  # Debug any validation errors
    else:
        form = CompanyForm()
    return render(request, 'add_company.html', {'form': form})

# Update a company
def update_company(request, pk):
    company = get_object_or_404(Company, pk=pk)
    if request.method == 'POST':
        form = CompanyForm(request.POST, instance=company)
        if form.is_valid():
            form.save()
            return redirect('company_list')  # Redirect to the company list
    else:
        form = CompanyForm(instance=company)
    return render(request, 'update_company.html', {'form': form, 'company': company})

# Delete a company
def delete_company(request, pk):
    company = get_object_or_404(Company, pk=pk)
    if request.method == "POST":
        company.delete()
        return redirect('company_list')  # Redirect to the company list after deletion
    return render(request, 'delete_company.html', {'company': company})






