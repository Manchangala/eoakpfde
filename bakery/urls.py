from django.contrib import admin
from django.urls import path, include
from bakery import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('menu/', views.menu, name='menu'),
    path('add_to_cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.view_cart, name='view_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('update_quantity/<int:item_id>/', views.update_quantity, name='update_quantity'),
    path('remove_from_cart/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('update_order_status/', views.update_order_status, name='update_order_status'),
    path('manage_products/', views.manage_products, name='manage_products'),
    path('add_product/', views.add_product, name='add_product'),
    path('edit_product/<int:product_id>/', views.edit_product, name='edit_product'),
    path('delete_product/<int:product_id>/', views.delete_product, name='delete_product'),
    path('reports/', views.reports, name='reports'),
    path('manage_orders/', views.manage_orders, name='manage_orders'),

]


