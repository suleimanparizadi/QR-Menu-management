from django.urls import path
from . import views

app_name = 'menu'

urlpatterns = [

    path('', views.MenuListView.as_view(), name='menu_list'),
    path('create/', views.MenuCreateView.as_view(), name='menu_create'),
    
    path('<int:menu_id>/', views.MenuDetailView.as_view(), name='menu_detail'),
    
    # adding items to a existing menu
    path('<int:menu_id>/items/', views.MenuItemAddView.as_view(), name='menu_add_item'),
    
    # deleting or updating an item
    path('<int:menu_id>/items/<int:item_id>/',
          views.MenuItemDetail.as_view(), name='item_detail'),

    # publicing menu for unauthenticated users
    path('public/<int:menu_id>/', views.PublicMenuView.as_view(),
         name='public_menu')


]


