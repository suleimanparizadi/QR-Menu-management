from django.test import TestCase
from rest_framework import serializers
from menu import serializers as menu_serializer
from django.contrib.auth import get_user_model
from menu.models import QRMenu, MenuItem, Category


User = get_user_model()

class QRMenuSerializerTest(TestCase):
    
    def setUp(self):
        self.user = User.objects.create_user(
            phone_number='09123456789',
            username='testowner',
            password='secure123'
        )

        self.valid_data = {
            'title': 'Test Menu',
            'description': 'Test description',
            'available': True 
        }



    def test_valid_data(self):

        serializer = menu_serializer.QRMneuCreateSerializer(
            data = self.valid_data,
            context = {'user':self.user}
        )

        self.assertTrue(serializer.is_valid())


    def test_create_menu(self):

        serializer = menu_serializer.QRMneuCreateSerializer(
            data=self.valid_data,
            context = {'user':self.user}

        )

        self.assertTrue(serializer.is_valid())
        menu = serializer.save()

        self.assertEqual(menu.title, 'Test Menu')
        self.assertEqual(menu.user, self.user)
        self.assertIsNotNone(menu.qr_code)



    def test_without_user_context(self):

        serializer = menu_serializer.QRMneuCreateSerializer(
            data=self.valid_data,
            context = {}
        )

        self.assertTrue(serializer.is_valid())

        with self.assertRaises(serializers.ValidationError):
            serializer.save()




class menuItemCreateSerializer(TestCase):

    def setUp(self):

        self.user = User.objects.create_user(
            phone_number='09123456789',
            username='testowner',
            password='secure123'
        )
        self.menu = QRMenu.objects.create(
            user=self.user,
            title='Test Menu'
        )
        self.category = Category.objects.create(name='Hot Drinks')

        self.valid_data = {
            'item': 'Espresso',
            'description': 'Strong coffee',
            'price': 50000,
            'category': self.category.id
        }       


    def test_valid_data(self):

        serializer = menu_serializer.MenuItemCreateSerializer(data=self.valid_data,
                                                             context={'menu':self.menu})
        

        self.assertTrue(serializer.is_valid())



    
    def test_create_item(self):

        serializer = menu_serializer.MenuItemCreateSerializer(
            data = self.valid_data,
            context = {'menu':self.menu}
        )
        self.assertTrue(serializer.is_valid())

        item = serializer.save()

        self.assertEqual(item.item, 'Espresso')
        self.assertEqual(item.menu, self.menu)
        self.assertEqual(item.price, 50000)



    def test_item_without_context(self):
        """Test error when no menu in context"""

        serializer = menu_serializer.MenuItemCreateSerializer(
            data = self.valid_data,
            context = {}
        )
        self.assertTrue(serializer.is_valid())    

        with self.assertRaises(serializers.ValidationError):
            serializer.save()



    def test_item_required(self):

        self.valid_data.pop('item')

        serializer = menu_serializer.MenuItemCreateSerializer(
            data=self.valid_data,
            context={'menu': self.menu}
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn('item', serializer.errors)



    def test_price_required(self):
        
        self.valid_data.pop('price')

        serializer = menu_serializer.MenuItemCreateSerializer(
            data=self.valid_data,
            context={'menu': self.menu}
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn('price', serializer.errors)


    
class BulkMenuItemSerializerTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            phone_number='09123456789',
            username='testowner',
            password='secure123'
        )
        self.menu = QRMenu.objects.create(
            user=self.user,
            title='Test Menu'
            )
            
        self.category = Category.objects.create(name='Hot Drinks')
        
        self.valid_data = {
            'items': [
                {'item': 'Espresso', 'price': 50000, 'category': self.category.id},
                {'item': 'Latte', 'price': 65000, 'category': self.category.id},
                {'item': 'Cappuccino', 'price': 60000},
            ]
        }


    def test_valid_bulk_data(self):

        serializer = menu_serializer.BulkMenuItemSerializer(
            data = self.valid_data,
            context = {'menu':self.menu}
        )
        self.assertTrue(serializer.is_valid())


    def test_bulk_creation_items(self):

        serializer = menu_serializer.BulkMenuItemSerializer(
            data = self.valid_data,
            context = {'menu':self.menu}
        )
        self.assertTrue(serializer.is_valid())

        items = serializer.save()
        self.assertEqual(len(items), 3)
        self.assertEqual(self.menu.items.count(), 3)


    def test_too_many_items_rejected(self):
        """Test more than 50 items fails"""
        data = {
            'items': [
                {'item': f'Item {i}', 'price': 10000} 
                for i in range(51)
            ]
        }
        serializer = menu_serializer.BulkMenuItemSerializer(
            data=data,
            context={'menu': self.menu}
        )
        self.assertFalse(serializer.is_valid())       

    


    def test_duplicate_items_rejected(self):
        """Test duplicate item names fail"""
        data = {
            'items': [
                {'item': 'Espresso', 'price': 50000},
                {'item': 'Espresso', 'price': 60000},  # Duplicate!
            ]
        }
        serializer = menu_serializer.BulkMenuItemSerializer(
            data=data,
            context={'menu': self.menu}
        )
        self.assertFalse(serializer.is_valid())


    def test_negative_price_rejected(self):
        """Test negative price fails"""
        data = {
            'items': [
                {'item': 'Espresso', 'price': -1000},
            ]
        }
        serializer = menu_serializer.BulkMenuItemSerializer(
            data=data,
            context={'menu': self.menu}
        )
        self.assertFalse(serializer.is_valid())


    def test_zero_price_rejected(self):
        """Test zero price fails"""
        data = {
            'items': [
                {'item': 'Free Item', 'price': 0},
            ]
        }
        serializer = menu_serializer.BulkMenuItemSerializer(
            data=data,
            context={'menu': self.menu}
        )
        self.assertFalse(serializer.is_valid())


    def test_price_too_high_rejected(self):
        """Test excessively high price fails"""
        data = {
            'items': [
                {'item': 'Expensive', 'price': 6000000},
            ]
        }
        serializer = menu_serializer.BulkMenuItemSerializer(
            data=data,
            context={'menu': self.menu}
        )
        self.assertFalse(serializer.is_valid())    


    def test_without_menu_context(self):
        """Test error when no menu in context"""
        serializer = menu_serializer.BulkMenuItemSerializer(
            data=self.valid_data,
            context={}
        )
        self.assertTrue(serializer.is_valid())
        
        with self.assertRaises(serializers.ValidationError):
            serializer.save()        



class QRMenuDetailSerializerTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            phone_number='09123456789',
            username='testowner',
            password='secure123'
        )
        self.menu = QRMenu.objects.create(
            user=self.user,
            title='Test Menu'
        )
        self.category = Category.objects.create(name='Hot Drinks', icon='☕')    

        MenuItem.objects.create(
            menu=self.menu,
            item='Espresso',
            price=50000,
            category=self.category
        )
        MenuItem.objects.create(
            menu=self.menu,
            item='Water',
            price=10000
        )



    def test_create_menu_with_items(self):
        """Test menu detail includes items"""

        serializer = menu_serializer.QRMenuDetailSerializer(self.menu)
        data = serializer.data

        self.assertEqual(data['title'], 'Test Menu')
        self.assertIn('items', data)
        self.assertIn('qr_code', data)

        


class QRMenuListSerializerTest(TestCase):
    
    def setUp(self):
        self.user = User.objects.create_user(
            phone_number='09123456789',
            username='testowner',
            password='secure123'
        )
        self.menu = QRMenu.objects.create(
            user=self.user,
            title='Test Menu'
        )

        MenuItem.objects.create(menu=self.menu, item='Item 1', price=10000)
        MenuItem.objects.create(menu=self.menu, item='Item 2', price=20000)    
    
    def test_items_count_field(self):
        """Test items_count is calculated"""
        serializer = menu_serializer.QRMenuListSerializer(self.menu)
        data = serializer.data
        
        self.assertEqual(data['items_count'], 2)


    def test_read_only_fields(self):
        """Test read-only fields are not writable"""

        data = {
            'title': 'New Title',
            'items_count': 999  # Should be ignored
        }
        serializer = menu_serializer.QRMenuListSerializer(
            self.menu, data=data, partial=True
        )
        self.assertTrue(serializer.is_valid())
        # items_count should still be 2 after update        
    