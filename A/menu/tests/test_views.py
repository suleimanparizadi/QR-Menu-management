from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from menu.models import QRMenu, MenuItem, Category
from django.contrib.auth import get_user_model

User = get_user_model()


class MenuCreateViewTest(TestCase):


    def setUp(self):
        
        self.client = APIClient()
        self.url = reverse('menu:menu_create')
        self.user = User.objects.create_user(
            phone_number='09123456789',
            username='testowner',
            password='secure123'
        )

        self._login()

    def _login(self):

        login_url = reverse('accounts:login_password')
        response = self.client.post(
            login_url,
            {'identifier': 'testowner',
            'password': 'secure123'},
            format='json'
        )
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {response.data["token"]}')




    def test_create_menu_success(self):
        """Create a menu without any items"""

        response = self.client.post(self.url, {
            'title': 'Test Menu',
            'description': 'Test description'
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


    def test_create_menu_with_items(self):
        """Create a menu with two different items"""

        response = self.client.post(self.url, {
            'title': 'Menu with Items',
            'items': [
                {'item': 'Item 1', 'price': 10000},
                {'item': 'Item 2', 'price': 20000},
            ]
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        menu = QRMenu.objects.get(title='Menu with Items')
        self.assertEqual(menu.items.count(), 2)


    def test_create_menu_invalid_items(self):
        """Test create a menu with invalid items"""
        response = self.client.post(self.url, {
            'title': 'Bad Menu',
            'items': [
                {'item': 'Bad Item', 'price': -100},  # Invalid price
            ]
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)    


    def test_unauthorized_fail(self):
        """Test create a menu without authentication"""

        new_client = APIClient()
        response = new_client.post(self.url, {'title': 'Test'}, format='json') 
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)



class MenuListView(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.url = reverse('menu:menu_list')
        self.user = User.objects.create_user(
            phone_number='09123456789',
            username='testowner',
            password='secure123'
        )
        self._login()

    def _login(self):
        login_url = reverse('accounts:login_password')
        response = self.client.post(login_url, {
            'identifier': 'testowner', 'password': 'secure123'
        }, format='json')
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {response.data["token"]}')        

        

    def test_list_menus(self):
        QRMenu.objects.create(user=self.user, title='Menu 1')
        QRMenu.objects.create(user=self.user, title='Menu 2')
        
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)        




class MenuDetailViewTest(TestCase):



    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            phone_number='09123456789', username='testowner', password='secure123'
        )

        self.menu = QRMenu.objects.create(user=self.user, title='Test Menu')
        self.url = reverse('menu:menu_detail', kwargs={'menu_id': self.menu.id})
        self._login()



    def _login(self):
        login_url = reverse('accounts:login_password')
        response = self.client.post(login_url, {
            'identifier': 'testowner', 'password': 'secure123'
        }, format='json')
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {response.data["token"]}')




    def test_get_menu(self):

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test Menu')

    
    def test_update_menu(self):
        response = self.client.put(self.url, {'title': 'Updated Menu'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.menu.refresh_from_db()
        self.assertEqual(self.menu.title, 'Updated Menu')


    def test_delete_menu(self):
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(QRMenu.objects.filter(id=self.menu.id).exists())        



class PublicMenuViewTest(TestCase):
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            phone_number='09123456789', username='testowner', password='secure123'
        )
        self.menu = QRMenu.objects.create(user=self.user, title='Public Menu', available=True)
        self.url = reverse('menu:public_menu', kwargs={'menu_id': self.menu.id})


    def test_unavailable_menu_not_shown(self):
        self.menu.available = False
        self.menu.save()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)        