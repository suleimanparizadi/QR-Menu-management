from rest_framework import serializers
from .models import QRMenu, MenuItem, Category


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for categories"""
    items_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'icon', 'items_count']
    
    def get_items_count(self, obj):
        return obj.items.count()



class QRMneuCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = QRMenu
        fields = ['title', 'description', 'available']

    def create(self, validated_data):
        # Get user from request (view) or directly (test)
        request = self.context.get('request')
        user = self.context.get('user')
        
        if request:
            user = request.user
        elif not user:
            raise serializers.ValidationError('User context is required')
        
        return QRMenu.objects.create(user=user, **validated_data)

class MenuItemSerializer(serializers.ModelSerializer):
    """Serializer for individual menu item"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = MenuItem
        fields = [
            'id', 'item', 'description', 'price', 
            'image', 'available', 'category', 'category_name'
        ]
        read_only_fields = ['id']


class MenuItemCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a single menu item"""
    
    class Meta:
        model = MenuItem
        fields = ['item', 'description', 'price', 'image', 'available', 'category']
    
    def create(self, validated_data):
        menu = self.context.get('menu')
        if not menu:
            raise serializers.ValidationError("Menu context is required.")
        return MenuItem.objects.create(menu=menu, **validated_data)


class BulkMenuItemSerializer(serializers.Serializer):
    """Serializer for creating multiple menu items at once"""
    items = MenuItemCreateSerializer(many=True)
    
    def validate_items(self, value):
        if not value:
            raise serializers.ValidationError("At least one item is required.")
        if len(value) > 50:
            raise serializers.ValidationError("Maximum 50 items per request.")
        
        # Check duplicates
        items_name = [item.get('item', '').lower() for item in value]
        if len(items_name) != len(set(items_name)):
            raise serializers.ValidationError('Duplicate items not allowed.')
        
        # Validate prices
        for item in value:
            price = item.get('price', 0)
            if price <= 0:
                raise serializers.ValidationError("Price must be greater than 0")
            if price > 5000000:
                raise serializers.ValidationError("Price seems too high")
        
        return value
    
    def create(self, validated_data):
        menu = self.context.get('menu')
        if not menu:
            raise serializers.ValidationError('Menu context is required')
        
        items_data = validated_data['items']
        menu_items = [
            MenuItem(menu=menu, **item_data)
            for item_data in items_data
        ]
        
        created_items = MenuItem.objects.bulk_create(menu_items)
        return created_items


class QRMenuDetailSerializer(serializers.ModelSerializer):
    """Serializer for viewing a single menu with items grouped by category"""
    items = serializers.SerializerMethodField()
    
    class Meta:
        model = QRMenu
        fields = [
            'id', 'title', 'description', 'qr_code',
            'available', 'items', 'created_at'
        ]
        read_only_fields = ['id', 'qr_code', 'created_at']
    
    def get_items(self, obj):
        """Return items grouped by category"""
        items = obj.items.select_related('category').all()
        
        # Group by category
        grouped = {}
        uncategorized = []
        
        for item in items:
            if item.category:
                cat_name = item.category.name
                if cat_name not in grouped:
                    grouped[cat_name] = {
                        'category_id': item.category.id,
                        'category_name': cat_name,
                        'category_icon': item.category.icon,
                        'items': []
                    }
                grouped[cat_name]['items'].append(MenuItemSerializer(item).data)
            else:
                uncategorized.append(MenuItemSerializer(item).data)
        
        result = list(grouped.values())
        if uncategorized:
            result.append({
                'category_name': 'Uncategorized',
                'category_icon': '📋',
                'items': uncategorized
            })
        
        return result
    

class QRMenuListSerializer(serializers.ModelSerializer):

    items_count = serializers.SerializerMethodField()

    class Meta:
        model = QRMenu
        fields = [
            'id', 'title', 'description', 'qr_code',
            'available', 'items_count', 'created_at'            
        ]
        read_only_fields = ['id', 'qr_code', 'created_at', 'items_count']

        # counts item in the menu
    def get_items_count(self, obj):

        # obj will be the menu 

        return obj.items.count()
        # and menu.items.count()




class QRMenuUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating exist menus"""

    class Meta:
        model = QRMenu
        fields = ['title', 'description', 'available']