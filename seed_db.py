import os
import django
from django.utils import timezone

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from security.models import ThreatLog

# Clear existing logs to start fresh
ThreatLog.objects.all().delete()

logs_to_create = [
    # Electron Website Attacks
    {"target": "electron", "ip": "192.168.1.10", "attack_type": "SQLi", "endpoint": "/api/v1/auth/login", "payload": "' OR 1=1 --", "user_agent": "Mozilla/5.0"},
    {"target": "electron", "ip": "192.168.1.11", "attack_type": "XSS", "endpoint": "/products/search", "payload": "<script>alert('XSS')</script>", "user_agent": "Mozilla/5.0"},
    {"target": "electron", "ip": "192.168.1.12", "attack_type": "Bruteforce", "endpoint": "/admin/login", "payload": "Multiple login attempts detected", "user_agent": "Hydra/9.0"},
    {"target": "electron", "ip": "192.168.1.13", "attack_type": "DDoS", "endpoint": "/", "payload": "Rapid request sequence from single source", "user_agent": "Unknown"},
    
    # Veloura Website Attacks (includes 'veloura' and 'fashion' targets)
    {"target": "veloura", "ip": "45.76.122.10", "attack_type": "SQLi", "endpoint": "/checkout", "payload": "'; DROP TABLE users; --", "user_agent": "Mozilla/5.0"},
    {"target": "fashion", "ip": "45.76.122.11", "attack_type": "XSS", "endpoint": "/reviews/post", "payload": "<img src=x onerror=alert(1)>", "user_agent": "Chrome/120.0"},
    {"target": "veloura", "ip": "45.76.122.12", "attack_type": "Bruteforce", "endpoint": "/api/users/signin", "payload": "50 failed attempts in 1 minute", "user_agent": "BurpSuite/2023.1"},
    {"target": "fashion", "ip": "45.76.122.13", "attack_type": "DDoS", "endpoint": "/api/health", "payload": "High volume traffic surge detected", "user_agent": "BotNet/v2"},
]

print(f"Starting to seed {len(logs_to_create)} threat logs...")

for log_data in logs_to_create:
    log = ThreatLog.objects.create(**log_data)
    print(f"Created {log.attack_type} log for {log.target} (ID: {log.id})")

print(f"\nSeeding complete. Total logs now: {ThreatLog.objects.count()}")
