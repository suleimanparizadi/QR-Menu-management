# menu/admin.py

from django.contrib import admin
from django.utils.html import format_html
from .models import QRMenu, MenuItem, Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon', 'items_count', 'created_at']
    search_fields = ['name']
    ordering = ['name']
    
    def items_count(self, obj):
        return obj.items.count()
    items_count.short_description = 'Number of Items'


class MenuItemInline(admin.TabularInline):
    """Show items inside the menu admin page"""
    model = MenuItem
    extra = 0  # No empty extra rows
    fields = ['item', 'category', 'price', 'available', 'image_preview']
    readonly_fields = ['image_preview']
    ordering = ['category__name', 'item']
    
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="50" height="50" style="border-radius:5px;" />',
                obj.image.url
            )
        return "No image"
    image_preview.short_description = 'Image'


@admin.register(QRMenu)
class QRMenuAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'user', 'items_count', 'available', 
        'qr_code_preview', 'created_at'
    ]
    list_filter = ['available', 'created_at']
    search_fields = ['title', 'description', 'user__username', 'user__phone_number']
    readonly_fields = ['qr_code_preview', 'created_at', 'qr_code_image']
    inlines = [MenuItemInline]
    
    fieldsets = (
        ('Menu Information', {
            'fields': ('user', 'title', 'description', 'available')
        }),
        ('QR Code', {
            'fields': ('qr_code', 'qr_code_preview'),
            'description': 'QR code is auto-generated when menu is created.'
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)  
        }),
    )
    
    def items_count(self, obj):
        return obj.items.count()
    items_count.short_description = 'Items'
    
    def qr_code_preview(self, obj):
        """Show a download link for QR code"""
        if obj.qr_code:
            return format_html(
                '<a href="{}" target="_blank">📱 Download QR Code</a>',
                obj.qr_code.url
            )
        return "No QR code generated yet"
    qr_code_preview.short_description = 'QR Code'
    
    def qr_code_image(self, obj):
        """Show QR code image preview"""
        if obj.qr_code:
            return format_html(
                '<img src="{}" width="150" height="150" style="border:1px solid #ddd;"/>',
                obj.qr_code.url
            )
        return "No QR code"
    qr_code_image.short_description = 'QR Code Preview'


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = [
        'item', 'menu', 'category', 'price_display', 
        'available', 'image_preview', 'created_at'
    ]
    list_filter = ['available', 'category', 'menu', 'created_at']
    search_fields = ['item', 'description', 'menu__title']
    readonly_fields = ['image_preview', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Item Information', {
            'fields': ('menu', 'category', 'item', 'description', 'price')
        }),
        ('Image', {
            'fields': ('image', 'image_preview'),
        }),
        ('Status', {
            'fields': ('available',),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    
    def price_display(self, obj):
        """Format price with commas"""
        return f"{obj.price:,} T"
    price_display.short_description = 'Price'
    price_display.admin_order_field = 'price' 
    
    def image_preview(self, obj):
        """Show thumbnail of item image"""
        if obj.image:
            return format_html(
                '<img src="{}" width="60" height="60" '
                'style="border-radius:8px; object-fit:cover;" />',
                obj.image.url
            )
        return format_html(
            '<span style="color:#999;">No image</span>'
        )
    image_preview.short_description = 'Image'


admin.site.site_header = 'QR Menu Administration'
admin.site.site_title = 'QR Menu Admin'
admin.site.index_title = 'Menu Management'