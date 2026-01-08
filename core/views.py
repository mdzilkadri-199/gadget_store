from django.shortcuts import render
from products.models import Product, Category
from django.db.models import Q

def home(request):
    # Get featured products
    featured_products = Product.objects.filter(is_active=True).order_by('?')[:8]
    
    # Get products by category
    categories = Category.objects.all()
    
    # Get new arrivals
    new_arrivals = Product.objects.filter(is_active=True).order_by('-created_at')[:4]
    
    context = {
        'featured_products': featured_products,
        'categories': categories,
        'new_arrivals': new_arrivals,
    }
    return render(request, 'core/home.html', context)

def search(request):
    query = request.GET.get('q', '')
    products = Product.objects.filter(is_active=True)
    
    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(category__name__icontains=query)
        )
    
    context = {
        'products': products,
        'query': query,
    }
    return render(request, 'products/product_list.html', context)