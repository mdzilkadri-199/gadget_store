from .models import Cart

def cart_context(request):
    """Context processor agar data keranjang tersedia di semua halaman (Navbar, Footer, dll)"""
    if request.user.is_authenticated:
        # Menggunakan get_or_create lebih ringkas daripada try-except manual
        cart, created = Cart.objects.get_or_create(user=request.user)
        
        return {
            'cart': cart,
            'cart_items': cart.items.all(), # untuk akses list produk
            'cart_items_count': cart.total_items # Menggunakan property total_items dari model Cart jika ada
        }
    
    return {
        'cart': None,
        'cart_items': [],
        'cart_items_count': 0
    }