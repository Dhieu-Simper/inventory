from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum, F, Q
from .models import Product, Supplier, Category, Sale, Purchase
from .forms import CategoryForm, SupplierForm, ProductForm


# DASHBOARD
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
        return redirect('category_list')
    return render(request, 'inventory/category_form.html', {'form': form, 'title': 'Add Category'})


def category_update(request, pk):
    category = get_object_or_404(Category, pk=pk)
    form = CategoryForm(request.POST or None, instance=category)
    if form.is_valid():
        form.save()
        return redirect('category_list')
    return render(request, 'inventory/category_form.html', {'form': form, 'title': 'Edit Category'})


def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        category.delete()
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
        return redirect('supplier_list')
    return render(request, 'inventory/supplier_form.html', {'form': form, 'title': 'Add Supplier'})


def supplier_update(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    form = SupplierForm(request.POST or None, instance=supplier)
    if form.is_valid():
        form.save()
        return redirect('supplier_list')
    return render(request, 'inventory/supplier_form.html', {'form': form, 'title': 'Edit Supplier'})


def supplier_delete(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    if request.method == 'POST':
        supplier.delete()
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
        return redirect('product_list')
    return render(request, 'inventory/product_form.html', {'form': form, 'title': 'Add Product'})


def product_update(request, pk):
    product = get_object_or_404(Product, pk=pk)
    form = ProductForm(request.POST or None, instance=product)
    if form.is_valid():
        form.save()
        return redirect('product_list')
    return render(request, 'inventory/product_form.html', {'form': form, 'title': 'Edit Product'})


def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        return redirect('product_list')
    return render(request, 'inventory/confirm_delete.html', {'object': product, 'type': 'Product'})