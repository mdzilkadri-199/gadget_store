# orders/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.OrderListView.as_view(), name='order_list'),
    path('admin/', views.AdminOrderListView.as_view(), name='admin_orders'),
    path('checkout/', views.checkout, name='checkout'),
    path('<int:order_id>/', views.OrderDetailView.as_view(), name='order_detail'),
    path('<int:order_id>/update-status/', 
         views.update_order_status, 
         name='update_order_status'),
    path('order/<int:order_id>/upload-receipt/', views.upload_payment_receipt, name='upload_payment_receipt'),
]