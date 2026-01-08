# Buat file initial_data.py di folder scripts/
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gadget_store.settings')
django.setup()

from products.models import Category, Product

# Create categories
categories = [
    {'name': 'Smartphone', 'slug': 'smartphone'},
    {'name': 'Tablet', 'slug': 'tablet'},
    {'name': 'Laptop', 'slug': 'laptop'},
    {'name': 'Aksesoris', 'slug': 'aksesoris'},
]

for cat_data in categories:
    Category.objects.get_or_create(**cat_data)

print("Data awal berhasil dibuat!")