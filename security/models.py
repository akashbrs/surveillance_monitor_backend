from django.db import models

# Create your models here.
from django.db import models


from django.db import models


class AttackLog(models.Model):
    ATTACK_TYPES = [
        ('SQLI', 'SQL Injection'),
        ('XSS', 'Cross Site Scripting'),
        ('DDOS', 'DDoS'),
        ('BRUTE', 'Brute Force'),
    ]

    attack_type = models.CharField(max_length=10, choices=ATTACK_TYPES)
    ip_address = models.GenericIPAddressField()
    target = models.CharField(max_length=100)  # Electron / Veloura
    timestamp = models.DateTimeField(auto_now_add=True)
    severity = models.CharField(max_length=20)
    status = models.CharField(max_length=20)  # Detected / Blocked
    payload = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.attack_type} from {self.ip_address} on {self.target}"

class BlockedIP(models.Model):
    ip_address = models.GenericIPAddressField(unique=True)
    reason = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)