from django.urls import path
from . import views

urlpatterns = [
    # Dashboard
    
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('', views.dashboard, name='dashboard'),

    # Categories
    path('categories/', views.category_list, name='category_list'),
    path('categories/add/', views.category_create, name='category_create'),
    path('categories/edit/<int:pk>/', views.category_update, name='category_update'),
    path('categories/delete/<int:pk>/', views.category_delete, name='category_delete'),

    # Suppliers
    path('suppliers/', views.supplier_list, name='supplier_list'),
    path('suppliers/add/', views.supplier_create, name='supplier_create'),
    path('suppliers/edit/<int:pk>/', views.supplier_update, name='supplier_update'),
    path('suppliers/delete/<int:pk>/', views.supplier_delete, name='supplier_delete'),

    # Products
    path('products/', views.product_list, name='product_list'),
    path('products/add/', views.product_create, name='product_create'),
    path('products/edit/<int:pk>/', views.product_update, name='product_update'),
    path('products/delete/<int:pk>/', views.product_delete, name='product_delete'),

    # Purchases
    path('purchases/', views.purchase_list, name='purchase_list'),
    path('purchases/add/', views.purchase_create, name='purchase_create'),

    # Sales
    path('sales/', views.sale_list, name='sale_list'),
    path('sales/add/', views.sale_create, name='sale_create'),
]