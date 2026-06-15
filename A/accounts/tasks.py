
from celery import shared_task
from django.utils import timezone
from datetime import timedelta

@shared_task
def remove_expired_otps():
    from accounts.models import OTP_Code  
    
    expired_time = timezone.now() - timedelta(minutes=5)
    count, _ = OTP_Code.objects.filter(created_at__lt=expired_time).delete()
    
    return f'Deleted {count} expired OTP codes'