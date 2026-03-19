from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum, F, Q
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm

from .models import Product, Supplier, Category, Sale, Purchase, PurchaseItem, SaleItem
from .forms import (
    CategoryForm, SupplierForm, ProductForm,
    PurchaseForm, PurchaseItemForm,
    SaleForm, SaleItemForm
)

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    form = AuthenticationForm(request, data=request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, 'inventory/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('login')
# DASHBOARD
@login_required(login_url='login')
def dashboard(request):
    total_products = Product.objects.count()
    total_suppliers = Supplier.objects.count()
    total_categories = Category.objects.count()
    total_sales = Sale.objects.aggregate(total=Sum('total_amount'))['total'] or 0
    total_purchases = Purchase.objects.aggregate(total=Sum('total_amount'))['total'] or 0
    low_stock_products = Product.objects.filter(quantity_in_stock__lte=F('reorder_level')).count()

    context = {
        'total_products': total_products,
        'total_suppliers': total_suppliers,
        'total_categories': total_categories,
        'total_sales': total_sales,
        'total_purchases': total_purchases,
        'low_stock_products': low_stock_products,
    }
    return render(request, 'inventory/dashboard.html', context)


# =========================
# CATEGORY CRUD
# =========================
def category_list(request):
    categories = Category.objects.all().order_by('-created_at')
    return render(request, 'inventory/category_list.html', {'categories': categories})


def category_create(request):
    form = CategoryForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, "Category added successfully.")
        return redirect('category_list')
    return render(request, 'inventory/category_form.html', {'form': form, 'title': 'Add Category'})


def category_update(request, pk):
    category = get_object_or_404(Category, pk=pk)
    form = CategoryForm(request.POST or None, instance=category)
    if form.is_valid():
        form.save()
        messages.success(request, "Category updated successfully.")
        return redirect('category_list')
    return render(request, 'inventory/category_form.html', {'form': form, 'title': 'Edit Category'})


def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        category.delete()
        messages.success(request, "Category deleted successfully.")
        return redirect('category_list')
    return render(request, 'inventory/confirm_delete.html', {'object': category, 'type': 'Category'})


# =========================
# SUPPLIER CRUD
# =========================
def supplier_list(request):
    suppliers = Supplier.objects.all().order_by('-created_at')
    return render(request, 'inventory/supplier_list.html', {'suppliers': suppliers})


def supplier_create(request):
    form = SupplierForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, "Supplier added successfully.")
        return redirect('supplier_list')
    return render(request, 'inventory/supplier_form.html', {'form': form, 'title': 'Add Supplier'})


def supplier_update(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    form = SupplierForm(request.POST or None, instance=supplier)
    if form.is_valid():
        form.save()
        messages.success(request, "Supplier updated successfully.")
        return redirect('supplier_list')
    return render(request, 'inventory/supplier_form.html', {'form': form, 'title': 'Edit Supplier'})


def supplier_delete(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    if request.method == 'POST':
        supplier.delete()
        messages.success(request, "Supplier deleted successfully.")
        return redirect('supplier_list')
    return render(request, 'inventory/confirm_delete.html', {'object': supplier, 'type': 'Supplier'})


# =========================
# PRODUCT CRUD
# =========================
def product_list(request):
    query = request.GET.get('q')
    products = Product.objects.select_related('category', 'supplier').all().order_by('-created_at')

    if query:
        products = products.filter(
            Q(product_name__icontains=query) |
            Q(sku__icontains=query) |
            Q(barcode__icontains=query) |
            Q(category__name__icontains=query)
        )

    return render(request, 'inventory/product_list.html', {
        'products': products,
        'query': query
    })


def product_create(request):
    form = ProductForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, "Product added successfully.")
        return redirect('product_list')
    return render(request, 'inventory/product_form.html', {'form': form, 'title': 'Add Product'})


def product_update(request, pk):
    product = get_object_or_404(Product, pk=pk)
    form = ProductForm(request.POST or None, instance=product)
    if form.is_valid():
        form.save()
        messages.success(request, "Product updated successfully.")
        return redirect('product_list')
    return render(request, 'inventory/product_form.html', {'form': form, 'title': 'Edit Product'})


def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        messages.success(request, "Product deleted successfully.")
        return redirect('product_list')
    return render(request, 'inventory/confirm_delete.html', {'object': product, 'type': 'Product'})


# =========================
# PURCHASES
# =========================
def purchase_list(request):
    purchases = Purchase.objects.select_related('supplier').all().order_by('-created_at')
    return render(request, 'inventory/purchase_list.html', {'purchases': purchases})


def purchase_create(request):
    purchase_form = PurchaseForm(request.POST or None)
    item_form = PurchaseItemForm(request.POST or None)

    if request.method == 'POST':
        if purchase_form.is_valid() and item_form.is_valid():
            purchase = purchase_form.save(commit=False)
            if request.user.is_authenticated:
                purchase.created_by = request.user
            purchase.save()

            purchase_item = item_form.save(commit=False)
            purchase_item.purchase = purchase
            purchase_item.total_cost = purchase_item.quantity * purchase_item.unit_cost
            purchase_item.save()

            # Update purchase total
            purchase.total_amount = purchase_item.total_cost
            purchase.save()

            # Increase stock
            product = purchase_item.product
            product.quantity_in_stock += purchase_item.quantity
            product.cost_price = purchase_item.unit_cost
            product.save()

            messages.success(request, "Purchase recorded successfully and stock updated.")
            return redirect('purchase_list')

    return render(request, 'inventory/purchase_form.html', {
        'purchase_form': purchase_form,
        'item_form': item_form,
        'title': 'Record Purchase'
    })


# =========================
# SALES
# =========================
def sale_list(request):
    sales = Sale.objects.all().order_by('-created_at')
    return render(request, 'inventory/sale_list.html', {'sales': sales})


def sale_create(request):
    sale_form = SaleForm(request.POST or None)
    item_form = SaleItemForm(request.POST or None)

    if request.method == 'POST':
        if sale_form.is_valid() and item_form.is_valid():
            sale_item = item_form.save(commit=False)
            product = sale_item.product

            # Prevent selling more than available stock
            if sale_item.quantity > product.quantity_in_stock:
                messages.error(request, f"Not enough stock for {product.product_name}. Available stock: {product.quantity_in_stock}")
            else:
                sale = sale_form.save(commit=False)
                if request.user.is_authenticated:
                    sale.created_by = request.user
                sale.save()

                sale_item.sale = sale
                sale_item.total_price = sale_item.quantity * sale_item.unit_price
                sale_item.save()

                # Update sale total
                sale.total_amount = sale_item.total_price
                sale.save()

                # Reduce stock
                product.quantity_in_stock -= sale_item.quantity
                product.save()

                messages.success(request, "Sale recorded successfully and stock updated.")
                return redirect('sale_list')

    return render(request, 'inventory/sale_form.html', {
        'sale_form': sale_form,
        'item_form': item_form,
        'title': 'Record Sale'
    })