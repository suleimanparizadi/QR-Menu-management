from rest_framework.response import Response
from rest_framework import permissions
from rest_framework.views import APIView
from .models import QRMenu, MenuItem
from django.shortcuts import get_object_or_404
from . import serializers



class MenuCreateView(APIView):

    """Create a menu with items in one request
    POST api/menus/"""

    permission_classes = [permissions.IsAuthenticated]



    def post(self, request):
        
        serializer = serializers.QRMneuCreateSerializer(data=request.data,
                                                         context={'request':request})
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)
        
        # menu created at serializer
        menu = serializer.save()


        #Create menu items too
        items_data = request.data.get('items', [])
        if items_data:
            item_serializer = serializers.BulkMenuItemSerializer(
                data={'items':items_data},
                context = {'menu':menu}

            )

            if not item_serializer.is_valid():

            

                return Response({'detail':'Menu created but items have errors. Add items later',
                                 'menu id':menu.id,
                                 'errors':item_serializer.errors
                                 },status=400)
            
            # create and save items if they are valid
            item_serializer.save()

        # return menu with QR code and with or without items_data 
        detailed_serilaizer = serializers.QRMenuDetailSerializer(menu)
        return Response(detailed_serilaizer.data, status=201)
    

class MenuListView(APIView):
    """List all menu's of the authenticated user"""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):

        menu = QRMenu.objects.filter(user=request.user)
        serializer = serializers.QRMenuListSerializer(menu, many=True)
        return Response(serializer.data)
    


class MenuDetailView(APIView):
    """View ,update and delete a specific menu
    GET    /api/menus/{menu_id}/
    PUT    /api/menus/{menu_id}/
    DELETE /api/menu/{menu_id}/
    """

    permission_classes = [permissions.IsAuthenticated]

    def get_menu(self, menu_id, user):

        return get_object_or_404(QRMenu,id=menu_id, user=user)


    def get(self, request, menu_id):

        menu = self.get_menu( menu_id=menu_id, user=request.user)
        serializer = serializers.QRMenuDetailSerializer(menu)
        return Response(serializer.data, status=200)
    

    def put(self, request, menu_id):

        menu = self.get_menu(menu_id, request.user)
        serializer = serializers.QRMenuUpdateSerializer(menu, 
                                                        data=request.data,
                                                        partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)
        
        serializer.save()
        detailed_serializer = serializers.QRMenuDetailSerializer(menu)
        return Response(detailed_serializer.data, status=200)


    def delete(self, request, menu_id):

        menu = self.get_menu(menu_id, request.user)

        menu.delete()
        return Response({'detail': 'Menu deleted successfully.'},
                         status=200)
    


class MenuItemAddView(APIView):
    """For adding up items to exited menu(single or bulk)
    POST /api/menu/{menu_id}/items/
    POST /api/menu/{menu_id}/items/bulk/
    """

    permission_classes = [permissions.IsAuthenticated]

    def get_menu(self, menu_id, user):

        return get_object_or_404(QRMenu, id=menu_id, user=user)


    def post(self, request, menu_id):

        menu = self.get_menu(user=request.user, menu_id=menu_id)


        if 'items' in request.data:
            # means there are multiple items and need bulk serialzer
            serializer = serializers.BulkMenuItemSerializer(
                data = request.data,
                context = {'menu':menu}
            )

        else:
            # means its just a single item

            serializer = serializers.MenuItemCreateSerializer(
                data=request.data,
                context = {'menu':menu}
            )

        if not serializer.is_valid():
            return Response(serializer.errors, status=400)
        
        items = serializer.save()


        # check if the items are list or single 
        if isinstance(items, list):
            # its a list many = True
            resualt_serializer = serializers.MenuItemSerializer(items, many=True)

        # its a single many = False
        resualt_serializer = serializers.MenuItemSerializer(items, many=True)

        return Response(resualt_serializer.data, status=201)        




class MenuItemDetail(APIView):
    """Update or delete a specific menu item
    
    PUT    /apt/menu/{menu_id}/items/{items_id}/
    DELETE /apt/menu/{menu_id}/items/{items_id}/
    """


    permission_classes = [permissions.IsAuthenticated]


    def get_item(self, menu_id, item_id, user):

        menu = get_object_or_404(QRMenu, user=user, id = menu_id)
        return get_object_or_404(MenuItem, menu=menu, id=item_id)
    

    def put(self, request, menu_id, item_id):

        item = self.get_item(menu_id, item_id, request.user)

        serializer = serializers.MenuItemSerializer(item,
                                                     data=request.data,
                                                       partial=True)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)
        

        serializer.save()

        return Response(serializer.data, status=200)
    



    def delete(self, request, menu_id, item_id):

        item = self.get_item(menu_id, item_id, request.user)

        item.delete()

        return Response({'detail':'Item deleted successfully'},
                         status=204)
    


class PublicMenuView(APIView):
    """Public view for scanning QR code"""
    """
    GET api/public/menu/{menu_id}
    """
    permission_classes = [permissions.AllowAny]


    def get(self, request, menu_id):

        menu = get_object_or_404(QRMenu, id=menu_id, available=True)

        serializer = serializers.QRMenuDetailSerializer(menu)

        return Response(serializer.data, status=200)





