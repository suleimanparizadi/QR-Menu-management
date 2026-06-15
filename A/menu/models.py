from django.db import models
from django.conf import settings
from django.core.files import File
from io import BytesIO 
import qrcode



class QRMenu(models.Model):

    user  = models.ForeignKey(settings.AUTH_USER_MODEL,
                               on_delete=models.CASCADE,
                               related_name='menus')

    title = models.CharField(max_length=225)
    description  = models.CharField(max_length=350, blank=True, null=True)
    qr_code = models.ImageField(upload_to='qr_menu', blank=True, null=True)
    available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)


    def generate_qr_code(self):
        """Generate QR code for this menu"""
        qr = qrcode.QRCode(version=1, box_size=10, border=2)
        qr.add_data(f"http://localhost:5173/menu/{self.id}")
        qr.make(fit=True)


        
        img = qr.make_image(fill_color="black", back_color="white")
        

        buffer = BytesIO()
        img.save(buffer, 'PNG')
        filename = f'menu_{self.id}_qr.png'
        self.qr_code.save(filename, File(buffer), save=False)
        buffer.close()    

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        if is_new and not self.qr_code:
            self.generate_qr_code()
            super().save(update_fields=['qr_code'])
        



    def __str__(self):
        return f"{self.title} - {self.user} - {self.id}"
    


    def delete(self, *args, **kwargs):
        if self.qr_code and self.qr_code.storage.exists(self.qr_code.name):
            self.qr_code.delete(save=False)
        super().delete(*args, **kwargs)


class Category(models.Model):

    name = models.CharField(max_length=125)
    description = models.CharField(max_length=225, null=True, blank=True)
    icon = models.CharField(max_length=50, null=True, blank=True, help_text='icon or emoji')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self):
        return self.name




class MenuItem(models.Model):
    
    menu = models.ForeignKey(QRMenu,
                              on_delete=models.CASCADE,
                                related_name='items')
    
    category = models.ForeignKey(Category,
                                  on_delete=models.SET_NULL,
                                  null=True,
                                    blank=True,
                                    related_name='items')
    
    item = models.CharField(max_length=225)
    description = models.CharField(max_length=335, blank=True, null=True)
    price = models.IntegerField()
    image = models.ImageField(upload_to='menu_item/', blank=True, null=True)
    available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    class Meta:
        ordering = ['category__name', 'item']


    def __str__(self):
        return f'{self.item} - {self.menu} - {self.id}'
    



