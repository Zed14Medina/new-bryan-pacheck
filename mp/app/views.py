from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import Group, User
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.db.models import Sum
from django.db import transaction

from .models import Product, Category, Cart, CartItem, Order, OrderDetail
from .forms import ProductForm, CheckoutForm, CustomUserCreationForm  # Import the CustomUserCreationForm

# Authentication Views
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('role_page')  # Redirect after successful login
        else:
            return render(request, 'app/login.html', {'error': 'Invalid credentials'})
    return render(request, 'app/login.html')

# User Signup View
def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)  # Use CustomUserCreationForm instead
        if form.is_valid():
            user = form.save()
            role = request.POST.get('role', 'Buyer')  # Get the role from the form
            
            # Create groups if they don't exist
            buyer_group, _ = Group.objects.get_or_create(name='Buyer')
            seller_group, _ = Group.objects.get_or_create(name='Seller')
            
            if role == 'Seller':
                user.groups.add(seller_group)
            else:
                user.groups.add(buyer_group)
                
            # Log the user in automatically
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)
            
            messages.success(request, f'Account created successfully! You are now logged in as a {role}.')
            return redirect('role_page')
        else:
            # If form has errors, display them to the user
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = CustomUserCreationForm()  # Use CustomUserCreationForm
    return render(request, 'app/signup.html', {'form': form})

# Add role switching functionality
@login_required
def switch_role(request):
    if request.method == 'POST':
        role = request.POST.get('role')
        user = request.user
        
        # Remove user from all role groups
        user.groups.clear()
        
        # Create groups if they don't exist
        buyer_group, _ = Group.objects.get_or_create(name='Buyer')
        seller_group, _ = Group.objects.get_or_create(name='Seller')
        
        # Add user to the selected group
        if role == 'Seller':
            user.groups.add(seller_group)
            messages.success(request, 'You are now a Seller!')
        else:
            user.groups.add(buyer_group)
            messages.success(request, 'You are now a Buyer!')
            
        return redirect('role_page')
    
    return render(request, 'app/switch_role.html')

# User Logout View
def logout_view(request):
    logout(request)
    return redirect('login')

def role_page(request):
    if request.user.is_authenticated:
        if request.user.groups.filter(name='Seller').exists():
            return redirect('seller_home')  # Redirect to seller home if the user is a seller
        elif request.user.groups.filter(name='Buyer').exists():
            return redirect('buyer_home')  # Redirect to buyer home if the user is a buyer
        else:
            return render(request, 'app/rolepage.html')  # Show the role selection page
    else:
        return redirect('login')

# Buyer and Seller Home Views
def buyer_home(request):  
    return render(request, 'app/buyer.html')

def seller_home(request):
    return render(request, 'app/seller.html')

# Helper function for seller check
def is_seller(user):
    return user.groups.filter(name='Seller').exists()

# Product Management Views (Seller)
@login_required
@user_passes_test(is_seller)
def seller_dashboard(request):
    products = Product.objects.filter(seller=request.user)
    return render(request, 'app/seller_dashboard.html', {'products': products})

@login_required
@user_passes_test(is_seller)
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.seller = request.user
            product.save()
            messages.success(request, 'Product added successfully!')
            return redirect('seller_dashboard')
    else:
        form = ProductForm()
    return render(request, 'app/add_product.html', {'form': form})

@login_required
@user_passes_test(is_seller)
def edit_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    
    # Verify the seller owns this product
    if product.seller != request.user:
        return HttpResponseForbidden("You don't have permission to edit this product")
        
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product updated successfully!')
            return redirect('seller_dashboard')
    else:
        form = ProductForm(instance=product)
    return render(request, 'app/edit_product.html', {'form': form})

@login_required
@user_passes_test(is_seller)
def delete_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    
    # Verify the seller owns this product
    if product.seller != request.user:
        return HttpResponseForbidden("You don't have permission to delete this product")
        
    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Product deleted successfully!')
        return redirect('seller_dashboard')
    return render(request, 'app/delete_product.html', {'product': product})

# Product Browsing Views
def product_list(request):
    category_id = request.GET.get('category')
    search_query = request.GET.get('search')
    
    products = Product.objects.all().filter(stock_quantity__gt=0)
    
    if category_id:
        products = products.filter(category_id=category_id)
        
    if search_query:
        products = products.filter(name__icontains=search_query)
    
    categories = Category.objects.all()
    
    context = {
        'products': products,
        'categories': categories,
        'selected_category': category_id,
        'search_query': search_query,
    }
    return render(request, 'app/product_list.html', context)

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    related_products = Product.objects.filter(category=product.category).exclude(id=product.id)[:4]
    
    context = {
        'product': product,
        'related_products': related_products,
    }
    return render(request, 'app/product_detail.html', context)

# Cart Management Views
@login_required
def cart_page(request):
    # Get or create user's cart
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = cart.items.all().select_related('product')
    
    context = {
        'cart': cart,
        'cart_items': cart_items,
    }
    return render(request, 'app/cart.html', context)

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart, created = Cart.objects.get_or_create(user=request.user)
    
    # Check if product is already in cart
    cart_item, item_created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'quantity': 1}
    )
    
    # If item already exists, increase quantity
    if not item_created:
        cart_item.quantity += 1
        cart_item.save()
    
    messages.success(request, f'{product.name} added to your cart.')
    return redirect('product_list')

@login_required
def update_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'increase':
            cart_item.quantity += 1
        elif action == 'decrease':
            if cart_item.quantity > 1:
                cart_item.quantity -= 1
            else:
                cart_item.delete()
                messages.success(request, 'Item removed from cart.')
                return redirect('cart_page')
        elif action == 'remove':
            cart_item.delete()
            messages.success(request, 'Item removed from cart.')
            return redirect('cart_page')
            
        cart_item.save()
        messages.success(request, 'Cart updated successfully.')
        
    return redirect('cart_page')

# Checkout and Order Processing Views
@login_required
def checkout_page(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = cart.items.all().select_related('product')
    
    if not cart_items:
        messages.warning(request, 'Your cart is empty. Please add products before checkout.')
        return redirect('product_list')
        
    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    # Create the order
                    shipping_address = form.cleaned_data['shipping_address']
                    total_price = cart.get_total_price()
                    
                    order = Order.objects.create(
                        user=request.user,
                        shipping_address=shipping_address,
                        total_price=total_price,
                        status='pending'
                    )
                    
                    # Add items to the order
                    for cart_item in cart_items:
                        OrderDetail.objects.create(
                            order=order,
                            product=cart_item.product,
                            quantity=cart_item.quantity
                        )
                        
                        # Update product stock
                        product = cart_item.product
                        product.stock_quantity -= cart_item.quantity
                        product.save()
                    
                    # Clear the cart
                    cart.items.all().delete()
                    
                    messages.success(request, f'Order #{order.id} placed successfully!')
                    return redirect('order_confirmation', order_id=order.id)
            except Exception as e:
                messages.error(request, f'Error processing order: {str(e)}')
    else:
        form = CheckoutForm()
        
    context = {
        'form': form,
        'cart': cart,
        'cart_items': cart_items,
    }
    return render(request, 'app/checkout.html', context)

@login_required
def order_confirmation(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    order_items = order.order_details.all().select_related('product')
    
    context = {
        'order': order,
        'order_items': order_items,
    }
    return render(request, 'app/order_confirmation.html', context)

@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'orders': orders,
    }
    return render(request, 'app/order_history.html', context)

@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    order_items = order.order_details.all().select_related('product')
    
    context = {
        'order': order,
        'order_items': order_items,
    }
    return render(request, 'app/order_detail.html', context)