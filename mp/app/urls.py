from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Authentication URLs
    path('', views.login_view, name='login'),  # Make login the default page
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    path('role/', views.role_selection, name='role_selection'),
    path('switch-role/', views.switch_role, name='switch_role'),
    
    # Buyer URLs
    path('buyer/', views.buyer_dashboard, name='buyer_dashboard'),
    path('products/', views.product_list, name='product_list'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('cart/', views.cart_page, name='cart_page'),
    path('update-cart/', views.update_cart, name='update_cart'),
    path('checkout/', views.checkout_page, name='checkout'),
    path('order/confirmation/<int:order_id>/', views.order_confirmation, name='order_confirmation'),
    path('order/detail/<int:order_id>/', views.order_detail, name='order_detail'),
    path('search/', views.search_products, name='search_products'),
    path('filter/', views.filter_products, name='filter_products'),
    
    # Seller URLs
    path('seller/', views.seller_dashboard, name='seller_dashboard'),
    path('seller/products/', views.product_list, name='seller_product_list'),
    path('seller/products/add/', views.add_product, name='add_product'),
    path('seller/products/<int:product_id>/edit/', views.edit_product, name='edit_product'),
    path('seller/products/<int:product_id>/delete/', views.delete_product, name='delete_product'),
    path('seller/orders/', views.seller_orders, name='seller_orders'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)