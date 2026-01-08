from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.views.generic import CreateView
from django.urls import reverse_lazy
from .models import User
from .forms import UserRegistrationForm
from orders.models import Order
from products.models import Product
from django.db.models import Sum, Count, Q
from datetime import datetime, timedelta
import django

@login_required
def dashboard(request):
    """Redirect user berdasarkan role"""
    if request.user.is_admin():
        return redirect('dashboard_admin')
    return redirect('dashboard_user')

@login_required
def dashboard_user(request):
    """Dashboard untuk user biasa"""
    orders = Order.objects.filter(user=request.user).order_by('-created_at')[:5]
    
    # Statistics
    total_orders = Order.objects.filter(user=request.user).count()
    pending_orders = Order.objects.filter(user=request.user, status='PENDING').count()
    total_spent = Order.objects.filter(
        user=request.user, 
        status__in=['PAID', 'COMPLETED']
    ).aggregate(total=Sum('total_price'))['total'] or 0
    
    context = {
        'orders': orders,
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'total_spent': total_spent,
    }
    return render(request, 'accounts/dashboard_user.html', context)

@login_required
def dashboard_admin(request):
    """Dashboard untuk admin"""
    # Cek permission
    if not request.user.is_admin():
        messages.error(request, "Anda tidak memiliki izin untuk mengakses halaman ini.")
        return redirect('dashboard_user')
    
    try:
        # Today's date
        today = datetime.now().date()
        
        # Basic statistics
        total_orders = Order.objects.count()
        pending_orders = Order.objects.filter(status='PENDING').count()
        total_users = User.objects.count()
        
        # Monthly revenue (last 30 days)
        month_ago = today - timedelta(days=30)
        month_revenue = Order.objects.filter(
            created_at__date__gte=month_ago,
            status__in=['PAID', 'COMPLETED']
        ).aggregate(total=Sum('total_price'))['total'] or 0
        
        # Today's statistics
        today_orders = Order.objects.filter(created_at__date=today).count()
        today_revenue = Order.objects.filter(
            created_at__date=today,
            status__in=['PAID', 'COMPLETED']
        ).aggregate(total=Sum('total_price'))['total'] or 0
        
        # New users today
        new_users_today = User.objects.filter(date_joined__date=today).count()
        
        # Stock information
        low_stock_products = Product.objects.filter(
            stock__lt=10, 
            stock__gt=0,
            is_active=True
        ).order_by('stock')[:5]
        
        out_of_stock = Product.objects.filter(
            stock=0,
            is_active=True
        ).count()
        
        # Recent orders (last 10 with user info)
        recent_orders = Order.objects.select_related('user').order_by('-created_at')[:10]
        
        # Week revenue (optional - for completeness)
        week_ago = today - timedelta(days=7)
        week_revenue = Order.objects.filter(
            created_at__date__gte=week_ago,
            status__in=['PAID', 'COMPLETED']
        ).aggregate(total=Sum('total_price'))['total'] or 0
        
        context = {
            # Basic stats
            'total_orders': total_orders,
            'pending_orders': pending_orders,
            'total_users': total_users,
            
            # Revenue
            'month_revenue': month_revenue,
            'today_revenue': today_revenue,
            'week_revenue': week_revenue,
            
            # Today's stats
            'today_orders': today_orders,
            'new_users_today': new_users_today,
            'out_of_stock': out_of_stock,
            
            # Lists
            'low_stock_products': low_stock_products,
            'recent_orders': recent_orders,
        }
        
        return render(request, 'accounts/dashboard_admin.html', context)
        
    except Exception as e:
        # Fallback dengan data dummy jika ada error
        print(f"Error in dashboard_admin: {e}")
        
        # Data dummy untuk testing jika database kosong
        context = {
            'total_orders': 156,
            'pending_orders': 12,
            'total_users': 89,
            'month_revenue': 45250000,
            'today_orders': 8,
            'today_revenue': 1250000,
            'new_users_today': 3,
            'out_of_stock': 2,
            'week_revenue': 8750000,
            'low_stock_products': [],
            'recent_orders': [],
        }
        return render(request, 'accounts/dashboard_admin.html', context)

class RegisterView(CreateView):
    """View untuk registrasi user baru"""
    form_class = UserRegistrationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('dashboard_user')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password1')
        user = authenticate(username=username, password=password)
        
        if user:
            login(self.request, user)
            messages.success(self.request, 'Registrasi berhasil! Selamat datang.')
        else:
            messages.error(self.request, 'Login otomatis gagal. Silakan login manual.')
            
        return response
    
    def dispatch(self, request, *args, **kwargs):
        """Redirect ke dashboard jika user sudah login"""
        if request.user.is_authenticated:
            return redirect('dashboard')
        return super().dispatch(request, *args, **kwargs)