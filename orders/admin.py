from django.contrib import admin, messages
from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    # Menambahkan product dan quantity agar admin bisa melihat detail barang yang dipesan
    readonly_fields = ['product', 'quantity', 'price']
    can_delete = False # Mencegah penghapusan item pesanan secara tidak sengaja

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    # Menambahkan payment_method agar admin tahu cara bayar user (COD/Transfer)
    list_display = ['order_number', 'user', 'status', 'payment_method', 'total_price', 'created_at']
    list_filter = ['status', 'payment_method', 'created_at']
    list_editable = ['status']
    search_fields = ['order_number', 'user__username']
    readonly_fields = ['order_number', 'user', 'created_at', 'updated_at']
    inlines = [OrderItemInline]
    
    # Menambahkan fitur Action untuk konfirmasi cepat secara massal
    actions = ['konfirmasi_pembayaran', 'tandai_dikirim', 'tandai_selesai']

    @admin.action(description='Konfirmasi: Tandai pesanan sudah DIBAYAR')
    def konfirmasi_pembayaran(self, request, queryset):
        updated = queryset.update(status='PAID')
        self.message_user(request, f'{updated} pesanan berhasil dikonfirmasi sebagai PAID.', messages.SUCCESS)

    @admin.action(description='Tandai pesanan sudah DIKIRIM')
    def tandai_dikirim(self, request, queryset):
        updated = queryset.update(status='SHIPPED')
        self.message_user(request, f'{updated} pesanan diubah ke SHIPPED.', messages.INFO)

    @admin.action(description='Tandai pesanan SELESAI')
    def tandai_selesai(self, request, queryset):
        updated = queryset.update(status='COMPLETED')
        self.message_user(request, f'{updated} pesanan diselesaikan.', messages.SUCCESS)

    fieldsets = (
        ('Informasi Pesanan', {
            'fields': ('order_number', 'user', 'status')
        }),
        ('Pengiriman', {
            'fields': ('shipping_address',)
        }),
        ('Pembayaran', {
            'fields': ('total_price', 'payment_method')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )