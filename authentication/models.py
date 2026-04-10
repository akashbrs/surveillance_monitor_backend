from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
import random

class OTPChallenge(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)

    @classmethod
    def generate_otp(cls, user):
        # Invalidate previous unverified OTPs
        cls.objects.filter(user=user, is_verified=False).delete()
        
        otp = str(random.randint(100000, 999999))
        return cls.objects.create(user=user, otp=otp)
    
    def is_valid(self):
        # Valid for 10 minutes
        return not self.is_verified and self.created_at >= timezone.now() - timedelta(minutes=10)
