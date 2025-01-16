from rest_framework import serializers
from .models import Product, Customer, CustomerTier, CustomerSpecificPrice, Order, OrderItem, Company

# Product Serializer
class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'  # Include all fields
        
# Company Serializer
class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = '__all__'  # Include all fields


# Customer Serializer
class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'


# Customer Tier Serializer
class CustomerTierSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerTier
        fields = '__all__'


# Customer Specific Price Serializer
class CustomerSpecificPriceSerializer(serializers.ModelSerializer):
    customer = serializers.StringRelatedField()  # Represent the customer as its `__str__` output
    product = serializers.StringRelatedField()  # Represent the product as its `__str__` output

    class Meta:
        model = CustomerSpecificPrice
        fields = '__all__'


# Order Item Serializer
class OrderItemSerializer(serializers.ModelSerializer):
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'quantity', 'price', 'total_price']

    def get_total_price(self, obj):
        return obj.quantity * obj.price  # Replace with your model's total price logic


# Order Serializer
class OrderSerializer(serializers.ModelSerializer):
    customer = serializers.PrimaryKeyRelatedField(queryset=Customer.objects.all())
    items = OrderItemSerializer(many=True)  # Allow nested writes
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ['id', 'customer', 'created_at', 'updated_at', 'items', 'total_price']

    def get_total_price(self, obj):
        return sum(item.quantity * item.price for item in obj.items.all())

    def create(self, validated_data):
        items_data = validated_data.pop('items')  # Extract nested items
        order = Order.objects.create(**validated_data)
        for item_data in items_data:
            OrderItem.objects.create(order=order, **item_data)
        return order

    def update(self, instance, validated_data):
        items_data = validated_data.pop('items', None)
        instance.customer = validated_data.get('customer', instance.customer)
        instance.save()

        if items_data:
            # Clear existing items and create new ones
            instance.items.all().delete()
            for item_data in items_data:
                OrderItem.objects.create(order=instance, **item_data)

        return instance

