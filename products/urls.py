# products/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.ProductListView.as_view(), name='product_list'),
    path('category/<slug:category_slug>/', 
         views.ProductListView.as_view(), 
         name='product_list_by_category'),
    path('<slug:slug>/', 
         views.ProductDetailView.as_view(), 
         name='product_detail'),
    
    # Admin URLs
    path('create/', views.ProductCreateView.as_view(), name='product_create'),
    path('<slug:slug>/update/', 
         views.ProductUpdateView.as_view(), 
         name='product_update'),
    path('<slug:slug>/delete/', 
         views.ProductDeleteView.as_view(), 
         name='product_delete'),
]