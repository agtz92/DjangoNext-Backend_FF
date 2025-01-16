from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from cotizador.views import ProductViewSet, CustomerViewSet, OrderViewSet, home
from . import views

# DRF Router for ViewSets
router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')
router.register(r'customers', CustomerViewSet, basename='customer')
router.register(r'orders', OrderViewSet, basename='order')

urlpatterns = [
    # API routes
    path('api/', include(router.urls)),  

    # Home route
    path('', home, name='home'),  
    
    # Product URLs
    path('products/', views.product_list, name='product_list'),
    path('products/add/', views.add_product, name='add_product'),
    path('products/<str:sku>/', views.product_detail, name='product_detail'),
    path('products/update/<str:sku>/', views.update_product, name='update_product'),
    path('products/<str:sku>/duplicate/', views.duplicate_product, name='duplicate_product'),
    path('products/<str:sku>/delete/', views.delete_product, name='delete_product'),

    # Customer URLs
    path('customers/', views.customer_list, name='customer_list'),
    path('customers/add/', views.add_customer, name='add_customer'),
    path('customers/<str:pk>/', views.customer_detail, name='customer_detail'),
    path('customers/<str:pk>/update/', views.update_customer, name='update_customer'),
    path('customers/<str:pk>/duplicate/', views.duplicate_customer, name='duplicate_customer'),
    path('customers/<str:pk>/delete/', views.delete_customer, name='delete_customer'),

    # Order URLs
    path('orders/', views.order_list, name='order_list'),
    path('orders/add/', views.add_order, name='add_order'),
    path('orders/<int:pk>/', views.order_detail, name='order_detail'),
    path('orders/<int:pk>/duplicate/', views.duplicate_order, name='duplicate_order'),
    path('orders/<int:pk>/update/', views.update_order, name='update_order'),
    path('orders/<int:pk>/delete/', views.delete_order, name='delete_order'), 
    #API Order URLS
    path('api/orders/create/', views.create_order, name='create_order'),  

    # Customer Specific Price URLs
    path('customer-prices/', views.customer_price_list, name='customer_price_list'),
    path('customer-prices/<int:pk>/', views.customer_price_detail, name='customer_price_detail'),
    
    #Company URLs
    path('companies/', views.company_list, name='company_list'),
    path('companies/add/', views.add_company, name='add_company'),
    path('companies/<uuid:pk>/update/', views.update_company, name='update_company'),
    path('companies/<uuid:pk>/delete/', views.delete_company, name='delete_company'),
    path('companies/<uuid:pk>/', views.company_detail, name='company_detail'),
]
