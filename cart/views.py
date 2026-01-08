from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from .models import Cart, CartItem
from products.models import Product

@login_required
def cart_detail(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    return render(request, 'cart/cart_detail.html', {'cart': cart})

@require_POST
@login_required
def add_to_cart(request):
    product_id = request.POST.get('product_id')
    quantity = int(request.POST.get('quantity', 1))
    
    product = get_object_or_404(Product, id=product_id)
    
    # Check stock
    if product.stock < quantity:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'message': f'Stok tidak mencukupi. Stok tersedia: {product.stock}'
            })
        messages.error(request, f'Stok tidak mencukupi. Stok tersedia: {product.stock}')
        return redirect('product_detail', slug=product.slug)
    
    cart, created = Cart.objects.get_or_create(user=request.user)
    
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'quantity': quantity}
    )
    
    if not created:
        cart_item.quantity += quantity
        cart_item.save()
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': 'Produk berhasil ditambahkan ke keranjang',
            'total_items': cart.total_items,
            'total_price': str(cart.total_price)
        })
    
    messages.success(request, 'Produk berhasil ditambahkan ke keranjang')
    return redirect('cart_detail')

@require_POST
@login_required
def update_cart_item(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    quantity = int(request.POST.get('quantity', 1))
    
    # Check stock
    if cart_item.product.stock < quantity:
        messages.error(request, f'Stok tidak mencukupi. Stok tersedia: {cart_item.product.stock}')
        return redirect('cart_detail')
    
    if quantity > 0:
        cart_item.quantity = quantity
        cart_item.save()
        messages.success(request, 'Jumlah produk berhasil diubah')
    else:
        cart_item.delete()
        messages.success(request, 'Produk dihapus dari keranjang')
    
    return redirect('cart_detail')

@require_POST
@login_required
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    cart_item.delete()
    messages.success(request, 'Produk dihapus dari keranjang')
    return redirect('cart_detail')

def cart_context(request):
    """Context processor untuk menambahkan cart ke semua template"""
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
        return {'cart': cart}
    return {'cart': None}