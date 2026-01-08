from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.urls import reverse_lazy
from .models import Product, Category

class ProductListView(ListView):
    model = Product
    template_name = 'products/product_list.html'
    context_object_name = 'products'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = Product.objects.filter(is_active=True)
        category_slug = self.kwargs.get('category_slug')
        if category_slug:
            category = get_object_or_404(Category, slug=category_slug)
            queryset = queryset.filter(category=category)
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context

class ProductDetailView(DetailView):
    model = Product
    template_name = 'products/product_detail.html'
    context_object_name = 'product'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['related_products'] = Product.objects.filter(
            category=self.object.category,
            is_active=True
        ).exclude(id=self.object.id)[:4]
        return context

class ProductCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Product
    template_name = 'products/product_form.html'
    fields = ['category', 'name', 'slug', 'description', 'price', 'stock', 'image', 'is_active']
    success_url = reverse_lazy('product_list')
    
    def test_func(self):
        return self.request.user.is_admin()
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, 'Produk berhasil ditambahkan!')
        return super().form_valid(form)

class ProductUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Product
    template_name = 'products/product_form.html'
    fields = ['category', 'name', 'slug', 'description', 'price', 'stock', 'image', 'is_active']
    success_url = reverse_lazy('product_list')
    
    def test_func(self):
        return self.request.user.is_admin()
    
    def form_valid(self, form):
        messages.success(self.request, 'Produk berhasil diperbarui!')
        return super().form_valid(form)

class ProductDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Product
    template_name = 'products/product_confirm_delete.html'
    success_url = reverse_lazy('product_list')
    
    def test_func(self):
        return self.request.user.is_admin()
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Produk berhasil dihapus!')
        return super().delete(request, *args, **kwargs)