from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import Group, User
from django.contrib import messages
from django.http import HttpResponseForbidden, JsonResponse
from django.db.models import Sum, Q
from django.db import transaction
from decimal import Decimal
import json

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
            return redirect('role_selection')  # Redirect after successful login
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
            return redirect('role_selection')
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
def role_selection(request):
    if request.user.is_authenticated:
        # Check if user already has a role
        if request.user.groups.filter(name='Seller').exists():
            return redirect('seller_dashboard')
        elif request.user.groups.filter(name='Buyer').exists():
            return redirect('buyer_dashboard')
        else:
            # User has no role, show role selection page
            return render(request, 'app/rolepage.html')
    else:
        return redirect('login')

@login_required
def switch_role(request):
    if request.method == 'POST':
        role = request.POST.get('role')
        user = request.user
        
        if role not in ['Buyer', 'Seller']:
            messages.error(request, 'Invalid role selected.')
            return redirect('role_selection')
        
        # Remove user from all role groups
        user.groups.clear()
        
        # Create groups if they don't exist
        buyer_group, _ = Group.objects.get_or_create(name='Buyer')
        seller_group, _ = Group.objects.get_or_create(name='Seller')
        
        # Add user to the selected group
        if role == 'Seller':
            user.groups.add(seller_group)
            messages.success(request, 'You are now a Seller!')
            return redirect('seller_dashboard')
        else:
            user.groups.add(buyer_group)
            messages.success(request, 'You are now a Buyer!')
            return redirect('buyer_dashboard')
    
    return redirect('role_selection')

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
    if not request.user.groups.filter(name='Seller').exists():
        messages.error(request, 'You must be a seller to access this page.')
        return redirect('role_selection')
    
    products = Product.objects.filter(seller=request.user)
    categories = Category.objects.all()
    
    context = {
        'products': products,
        'categories': categories,
        'user': request.user
    }
    return render(request, 'app/seller.html', context)

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

@login_required
def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    related_products = Product.objects.filter(category=product.category).exclude(id=product_id)[:4]
    context = {
        'product': product,
        'related_products': related_products
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
    
    try:
        # Check if the product is already in the cart
        cart_item = CartItem.objects.get(cart=cart, product=product)
        # If it exists, increase the quantity
        cart_item.quantity += 1
        cart_item.save()
        messages.success(request, f'{product.name} quantity updated in your cart.')
    except CartItem.DoesNotExist:
        # If the item is not in the cart, create a new cart item
        CartItem.objects.create(cart=cart, product=product, quantity=1)
        messages.success(request, f'{product.name} added to your cart.')
    
    messages.success(request, f'{product.name} added to your cart.')
    return redirect('product_list')

@login_required
def update_cart(request):
    if request.method == 'POST':
        try:
            cart, created = Cart.objects.get_or_create(user=request.user)
            print(f"DEBUG: Initial cart items for user {request.user.username}: {cart.items.all()}")

            data = json.loads(request.body)
            product_id = data.get('product_id')
            quantity = int(data.get('quantity', 1))
            action = data.get('action')

            if action == 'add':
                product = get_object_or_404(Product, id=product_id)
                cart_item, created = CartItem.objects.get_or_create(
                    cart=cart,
                    product=product,
                    defaults={'quantity': quantity}
                )
                if not created:
                    cart_item.quantity += quantity
                    cart_item.save()
            elif action == 'update':
                product = get_object_or_404(Product, id=product_id)
                cart_item = get_object_or_create(CartItem, cart=cart, product=product)
                cart_item.quantity = quantity
                cart_item.save()
            elif action == 'remove':
                product = get_object_or_404(Product, id=product_id)
                CartItem.objects.filter(cart=cart, product=product).delete()
            elif action == 'clear':
                cart.items.all().delete()
                messages.info(request, 'Your cart has been cleared.')

            # Recalculate cart total
            cart_items = CartItem.objects.filter(cart=cart)
            total = sum(item.product.price * item.quantity for item in cart_items)

            print(f"DEBUG: Cart items in update_cart: {cart_items}")
            print(f"DEBUG: Calculated total in update_cart: {total}")

            cart.total_price = total
            cart.save()

            # Get the updated cart item to return its details
            updated_cart_item = None
            if product_id:
                try:
                    product = Product.objects.get(id=product_id)
                    updated_cart_item = CartItem.objects.filter(cart=cart, product=product).first()
                except Product.DoesNotExist:
                    pass

            return JsonResponse({
                'status': 'success',
                'cart_total': float(cart.total_price),
                'cart_count': cart_items.count(),
                'item_id': updated_cart_item.id if updated_cart_item else None,
                'quantity': updated_cart_item.quantity if updated_cart_item else 0,
                'item_total': float(updated_cart_item.get_total()) if updated_cart_item else 0.00,
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)

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
    if request.method == 'POST':
        form = CheckoutForm(request.POST, instance=order)
        if form.is_valid():
            order = form.save(commit=False)
            order.status = 'confirmed'
            order.save()
            
            # Clear the cart after successful order
            Cart.objects.filter(user=request.user).delete()
            
            messages.success(request, 'Order confirmed successfully!')
            return redirect('order_detail', order_id=order.id)
    else:
        form = CheckoutForm(instance=order)
    
    return render(request, 'app/order_confirmation.html', {
        'order': order,
        'form': form
    })

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
    order_items = OrderDetail.objects.filter(order=order)
    
    return render(request, 'app/order_detail.html', {
        'order': order,
        'order_items': order_items
    })

@login_required
def search_products(request):
    query = request.GET.get('q', '')
    if query:
        products = Product.objects.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(category__name__icontains=query)
        ).filter(is_active=True)
    else:
        products = Product.objects.filter(is_active=True)
    
    context = {
        'products': products,
        'query': query
    }
    return render(request, 'app/buyer.html', context)

@login_required
def filter_products(request):
    category_id = request.GET.get('category')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    
    products = Product.objects.filter(is_active=True)
    
    if category_id:
        products = products.filter(category_id=category_id)
    if min_price:
        products = products.filter(price__gte=Decimal(min_price))
    if max_price:
        products = products.filter(price__lte=Decimal(max_price))
    
    context = {
        'products': products,
        'categories': Category.objects.all(),
        'selected_category': category_id,
        'min_price': min_price,
        'max_price': max_price
    }
    return render(request, 'app/buyer.html', context)

@login_required
def buyer_dashboard(request):
    if not request.user.groups.filter(name='Buyer').exists():
        messages.error(request, 'You must be a buyer to access this page.')
        return redirect('role_selection')
    
    products = Product.objects.filter(is_active=True)
    categories = Category.objects.all()
    
    context = {
        'products': products,
        'categories': categories,
        'user': request.user
    }
    return render(request, 'app/buyer.html', context)

@login_required
def seller_orders(request):
    # Placeholder implementation
    # You can later implement order management for sellers here
    return render(request, 'app/seller_orders.html', {})