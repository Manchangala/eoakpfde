# urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('manage_orders/', views.manage_orders, name='manage_orders'),
    path('manage_products/', views.manage_products, name='manage_products'),
    path('add_product/', views.add_product, name='add_product'),
    path('reports/', views.reports, name='reports'),
    path('confirm_order/', views.confirm_order, name='confirm_order'),
    path('order_success/', views.order_success, name='order_success'),
]
