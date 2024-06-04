# bakery/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Product, Order, OrderItem, Customer
from .forms import ProductForm, OrderForm, ReportForm, CustomUserCreationForm

def home(request):
    if request.user.is_authenticated:
        return redirect('menu')
    return render(request, 'bakery/home.html')

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            Customer.objects.create(
                user=user,
                first_name=form.cleaned_data.get('first_name'),
                last_name=form.cleaned_data.get('last_name'),
                phone=form.cleaned_data.get('phone'),
                address=form.cleaned_data.get('address')
            )
            messages.success(request, 'Registration successful. Please log in.')
            return redirect('login')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CustomUserCreationForm()
    return render(request, 'bakery/register.html', {'form': form})

@login_required
def menu(request):
    products = Product.objects.all()
    return render(request, 'bakery/menu.html', {'products': products, 'step': 1})

@login_required
def add_to_cart(request, product_id):
    try:
        customer = request.user.customer
    except Customer.DoesNotExist:
        messages.error(request, "User has no customer associated.")
        return redirect('menu')

    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get('quantity', 1))
    order, created = Order.objects.get_or_create(customer=customer, is_delivered=False)
    order_item, created = OrderItem.objects.get_or_create(order=order, product=product, defaults={'quantity': quantity, 'price': product.price})
    if not created:
        order_item.quantity += quantity
        order_item.save()
    messages.success(request, f'{product.name} added to cart.')
    return redirect('menu')

@login_required
def view_cart(request):
    order = Order.objects.filter(customer=request.user.customer, is_delivered=False).first()
    return render(request, 'bakery/cart.html', {'order': order, 'step': 2})

@login_required
def confirm_order(request):
    if request.method == "POST":
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.customer = request.user.customer
            order.save()
            # Add logic to associate order items with this order
            return redirect('order_success')
    else:
        form = OrderForm()
    return render(request, 'bakery/confirm_order.html', {'form': form})

@login_required
def order_success(request):
    return render(request, 'bakery/order_success.html')



@login_required
def delivery_options(request):
    order = get_object_or_404(Order, customer=request.user.customer, is_delivered=False)
    if request.method == 'POST':
        order.delivery_option = request.POST.get('delivery_option')
        order.save()
        return redirect('checkout')
    return render(request, 'bakery/delivery_options.html', {'order': order, 'step': 3})

@login_required
def checkout(request):
    order = get_object_or_404(Order, customer=request.user.customer, is_delivered=False)
    if request.method == 'POST':
        order.is_delivered = True
        order.save()
        messages.success(request, 'Order has been placed successfully.')
        return redirect('menu')
    return render(request, 'bakery/checkout.html', {'order': order, 'step': 4})

@login_required
def update_quantity(request, item_id):
    item = get_object_or_404(OrderItem, id=item_id, order__customer=request.user.customer, order__is_delivered=False)
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity'))
        item.quantity = quantity
        item.save()
        messages.success(request, f'Updated {item.product.name} quantity to {item.quantity}.')
    return redirect('view_cart')

@login_required
def remove_from_cart(request, item_id):
    item = get_object_or_404(OrderItem, id=item_id, order__customer=request.user.customer, order__is_delivered=False)
    item.delete()
    messages.success(request, f'Removed {item.product.name} from cart.')
    return redirect('view_cart')


# bakery/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from .models import Product, Order, OrderItem, Customer, Category
from .forms import ProductForm, OrderForm, ReportForm
from django.db.models import Count, Sum
from django.utils.dateparse import parse_date

def is_admin(user):
    return user.is_staff

@user_passes_test(is_admin)
def admin_dashboard(request):
    return render(request, 'bakery/admin_dashboard.html')


@user_passes_test(is_admin)
def manage_orders(request):
    orders = Order.objects.all()
    return render(request, 'bakery/manage_orders.html', {'orders': orders})


@user_passes_test(is_admin)
def manage_products(request):
    products = Product.objects.all()
    return render(request, 'bakery/manage_products.html', {'products': products})

@user_passes_test(is_admin)
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('manage_products')
    else:
        form = ProductForm()
    return render(request, 'bakery/add_product.html', {'form': form})

@user_passes_test(is_admin)
def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product updated successfully.')
            return redirect('manage_products')
    else:
        form = ProductForm(instance=product)
    return render(request, 'bakery/edit_product.html', {'form': form})

@user_passes_test(is_admin)
def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Product deleted successfully.')
        return redirect('manage_products')
    return render(request, 'bakery/delete_product.html', {'product': product})

@user_passes_test(is_admin)
def reports(request):
    form = ReportForm(request.GET or None)
    orders = Order.objects.all()
    order_items = OrderItem.objects.all()
    total_orders = orders.count()
    total_revenue = order_items.aggregate(total=Sum('price'))['total'] or 0
    top_products = order_items.values('product__name').annotate(count=Count('product')).order_by('-count')[:5]

    context = {
        'form': form,
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'top_products': top_products,
    }
    return render(request, 'bakery/reports.html', context)

@user_passes_test(is_admin)
def update_order_status(request):
    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        new_status = request.POST.get('new_status')
        order = get_object_or_404(Order, id=order_id)
        order.is_delivered = new_status == 'delivered'
        order.save()
        return redirect('manage_orders')
    return redirect('manage_orders')