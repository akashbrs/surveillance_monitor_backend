from django.db import models

# Create your models here.
from django.db import models


from django.db import models


class ThreatLog(models.Model):
    target = models.CharField(max_length=100)   # 🔥 NEW (MAIN FIELD)

    ip = models.CharField(max_length=100)
    attack_type = models.CharField(max_length=20)
    endpoint = models.CharField(max_length=255,blank=True,null = True)
    payload = models.TextField(blank=True)
    user_agent = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    resolved = models.BooleanField(default=False)
    ignored = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.target} - {self.ip} - {self.attack_type}"


class BlockedIP(models.Model):
    ip_address = models.GenericIPAddressField(unique=True)
    reason = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)