from django.test import TestCase
from menu.models import QRMenu, MenuItem, Category
from django.contrib.auth import get_user_model


User = get_user_model()



class QRMenuModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            phone_number='09123456789',
            username='testowner',
            password='secure123'
        )


    def test_create_menu(self):

        menu = QRMenu.objects.create(
            user=self.user,
            title="test menu",
            description="test description"
        )

        self.assertEqual(menu.title, 'test menu')
        self.assertEqual(menu.user, self.user)
        self.assertTrue(menu.available)
        self.assertIsNotNone(menu.created_at)


    def test_qr_code_generated(self):

        menu = QRMenu.objects.create(
            user=self.user,
            title="QR Test Menu"
        ) 

        self.assertIsNotNone(menu.qr_code)
        self.assertTrue(menu.qr_code.name.startswith('qr_menu/'))



    def test_menu_belong_to_user(self):
        """Test if the new menu is on the users menu list or not"""
        menu = QRMenu.objects.create(
            user=self.user,
            title="QR Test Menu"
        ) 

        self.assertIn(menu, self.user.menus.all())



    def test_delete_menu_remove_qr_code(self):  
        """Test QR code file is deleted with menu"""
        
        menu = QRMenu.objects.create(
            user=self.user,
            title="Delete Test"
        )

        qr_path = menu.qr_code.path
        self.assertTrue(menu.qr_code.storage.exists(qr_path))

        menu.delete()
        self.assertFalse(menu.qr_code.storage.exists(qr_path))
       



class MenuItemTest(TestCase):


    def setUp(self):
        self.user = User.objects.create_user(
            phone_number = '09123456789',
            username='testuser',
            password='secure1234'
        )

        self.menu = QRMenu.objects.create(
            user = self.user,
            title = 'Test Menu'
        )

        self.category = Category.objects.create(
            name = 'Hot',
            icon = '☕'
        )

    
    def test_cratea_item(self):

        item = MenuItem.objects.create(
            menu = self.menu,
            item = 'Coffee',
            description = 'nice Coffee',
            price = 50000,
            category = self.category 
        )


        self.assertEqual(item.item, 'Coffee')
        self.assertEqual(item.menu, self.menu)
        self.assertEqual(item.price, 50000)
        self.assertTrue(item.available)




    def test_item_belong_menu(self):

        item = MenuItem.objects.create(
            menu = self.menu,
            item = 'Coffee',
            description = 'nice Coffee',
            price = 50000,
            category = self.category 
        )

        self.assertIn(item, self.menu.items.all())


    
    def test_item_belong_category(self):

        item = MenuItem.objects.create(
            menu = self.menu,
            item = 'Coffee',
            description = 'nice Coffee',
            price = 50000,
            category = self.category 
        )


        self.assertEqual(item.category, self.category)
        self.assertEqual(item.category.name, 'Hot')
        self.assertEqual(item.category.icon, '☕')



    def test_item_without_category(self):
        """Test items can create without categories"""

        item = MenuItem.objects.create(
            menu = self.menu,
            item = 'Coffee',
            description = 'nice Coffee',
            price = 50000,
        )       


        self.assertIsNone(item.category)


    def test_bulk_create_item(self):
        """Testing bulk creating items"""

        items = [
            MenuItem(menu=self.menu, item="Item 1", price=10000),
            MenuItem(menu=self.menu, item="Item 2", price=20000),
            MenuItem(menu=self.menu, item="Item 3", price=30000),            
        ]

        created = MenuItem.objects.bulk_create(items)

        self.assertEqual(len(created), 3)
        self.assertEqual(self.menu.items.count(), 3)
                        # create a query on data base to count items
                    # SELECT COUNT(*) FROM menu_item WHERE menu_id = 1;


    def test_default_available_true(self):


        item = MenuItem.objects.create(
            menu = self.menu,
            item = 'Coffee',
            description = 'nice Coffee',
            price = 50000,
            category = self.category 
        )
        self.assertTrue(item.available)
        