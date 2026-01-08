from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .models import Order, OrderItem
from cart.models import Cart
from django.db import transaction

@login_required
def checkout(request):
    try:
        cart = Cart.objects.get(user=request.user)
    except Cart.DoesNotExist:
        cart = Cart.objects.create(user=request.user)
    
    if cart.total_items == 0:
        messages.warning(request, "Keranjang Anda kosong!")
        return redirect('cart_detail')
    
    if request.method == 'POST':
        # 1. Ambil data lengkap dari form checkout.html
        shipping_address = request.POST.get('shipping_address')
        full_name = request.POST.get('full_name')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        city = request.POST.get('city')
        postal_code = request.POST.get('postal_code')
        notes = request.POST.get('notes')
        payment_method = request.POST.get('payment_method', 'bank_transfer')
        
        # 2. Validasi stok sebelum memproses transaksi
        for item in cart.items.all():
            if item.product.stock < item.quantity:
                messages.error(request, 
                    f'Stok {item.product.name} tidak mencukupi. '
                    f'Stok tersedia: {item.product.stock}, '
                    f'Jumlah diminta: {item.quantity}')
                return redirect('cart_detail')
        
        # 3. Format alamat lengkap untuk disimpan di database
        complete_address = f"""
        {full_name}
        {phone}
        {email}
        {shipping_address}
        {city} {postal_code}
        
        Catatan: {notes if notes else '-'}
        Metode Pembayaran: {payment_method}
        """
        
        # 4. Hitung rincian biaya tambahan
        shipping_fee = 15000
        service_fee = 2000
        cod_fee = 5000 if payment_method == 'cod' else 0
        total_price = cart.total_price + shipping_fee + service_fee + cod_fee
        
        # 5. Eksekusi penyimpanan dengan Atomic Transaction (Aman)
        with transaction.atomic():
            order = Order.objects.create(
                user=request.user,
                shipping_address=complete_address,
                total_price=total_price,
                payment_method=payment_method
            )
            
            # Buat item pesanan dan potong stok produk
            for cart_item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    quantity=cart_item.quantity,
                    price=cart_item.product.price
                )
                
                # Update product stock
                cart_item.product.stock -= cart_item.quantity
                cart_item.product.save()
            
            # Kosongkan keranjang setelah berhasil checkout
            cart.items.all().delete()
        
        messages.success(request, f"Pesanan #{order.order_number} berhasil dibuat!")
        return redirect('order_detail', order_id=order.id)
    
    # Untuk GET request, tampilkan form
    return render(request, 'orders/checkout.html', {'cart': cart})

# --- Class Based Views di bawah ini tetap sama ---

class OrderListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'orders/order_list.html'
    context_object_name = 'orders'
    paginate_by = 10
    
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by('-created_at')

class OrderDetailView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = 'orders/order_detail.html'
    context_object_name = 'order'
    pk_url_kwarg = 'order_id'
    
    def get_queryset(self):
        if self.request.user.is_admin():
            return Order.objects.all()
        return Order.objects.filter(user=self.request.user)

@login_required
def update_order_status(request, order_id):
    if not request.user.is_admin():
        return redirect('dashboard_user')
    
    order = get_object_or_404(Order, id=order_id)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Order.STATUS_CHOICES):
            order.status = new_status
            order.save()
            messages.success(request, f"Status pesanan #{order.order_number} diperbarui menjadi {order.get_status_display()}")
    # Mengarahkan kembali ke dashboard admin jika aksi dilakukan dari sana
    return redirect(request.META.get('HTTP_REFERER', 'dashboard_admin'))
    

class AdminOrderListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Order
    template_name = 'orders/admin_order_list.html'
    context_object_name = 'orders'
    paginate_by = 20
    
    def test_func(self):
        return self.request.user.is_admin()
    
    def get_queryset(self):
        status = self.request.GET.get('status', '')
        if status:
            return Order.objects.filter(status=status).order_by('-created_at')
        return Order.objects.all().order_by('-created_at')
    
# Tambahkan fungsi ini di orders/views.py

@login_required
def upload_payment_receipt(request, order_id):
    if request.method == 'POST':
        # Pastikan pesanan milik user yang sedang login atau user adalah admin
        if request.user.is_admin():
            order = get_object_or_404(Order, id=order_id)
        else:
            order = get_object_or_404(Order, id=order_id, user=request.user)
            
        receipt = request.FILES.get('receipt')
        
        if receipt:
            order.payment_receipt = receipt # Pastikan field ini ada di model Order
            order.save()
            messages.success(request, 'Bukti pembayaran berhasil diunggah. Mohon tunggu verifikasi admin.')
        else:
            messages.error(request, 'Gagal mengunggah. Silakan pilih file gambar terlebih dahulu.')
            
    return redirect('order_detail', order_id=order_id)