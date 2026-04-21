import os
import django
from django.utils import timezone

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from security.models import AttackLog

# Clear existing logs to start fresh
AttackLog.objects.all().delete()

logs_to_create = [
    # Electron Website Attacks
    {"target": "Electron Website", "ip_address": "192.168.1.10", "attack_type": "SQLI", "severity": "Critical", "status": "Blocked", "payload": "' OR 1=1 --"},
    {"target": "Electron Website", "ip_address": "192.168.1.11", "attack_type": "XSS", "severity": "High", "status": "Detected", "payload": "<script>alert('XSS')</script>"},
    {"target": "Electron Website", "ip_address": "192.168.1.12", "attack_type": "BRUTE", "severity": "High", "status": "Logged", "payload": "5 failed login attempts"},
    {"target": "Electron Website", "ip_address": "192.168.1.13", "attack_type": "DDOS", "severity": "Critical", "status": "Blocked", "payload": "Rate limit exceeded (150 req/min)"},
    
    # Veloura Website Attacks
    {"target": "Veloura Website", "ip_address": "45.76.122.10", "attack_type": "SQLI", "severity": "Critical", "status": "Blocked", "payload": "'; DROP TABLE users; --"},
    {"target": "Veloura Website", "ip_address": "45.76.122.11", "attack_type": "XSS", "severity": "High", "status": "Detected", "payload": "<img src=x onerror=alert(1)>"},
    {"target": "Veloura Website", "ip_address": "45.76.122.12", "attack_type": "BRUTE", "severity": "High", "status": "Logged", "payload": "10 failed login attempts"},
    {"target": "Veloura Website", "ip_address": "45.76.122.13", "attack_type": "DDOS", "severity": "Critical", "status": "Blocked", "payload": "Volumetric flow surge"},
]

print(f"Starting to seed {len(logs_to_create)} attack logs...")

for log_data in logs_to_create:
    log = AttackLog.objects.create(**log_data)
    print(f"Created {log.attack_type} log for {log.target} (ID: {log.id})")

print(f"\nSeeding complete. Total logs now: {AttackLog.objects.count()}")
