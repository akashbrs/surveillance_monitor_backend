import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from security.models import ThreatLog

print("Creating test log...")
log = ThreatLog.objects.create(
    target="electron",
    ip="1.2.3.4",
    attack_type="SQL Injection",
    endpoint="/api/test",
    payload="OR 1=1",
    user_agent="TestAgent"
)
print(f"Created log with ID: {log.id}")
print(f"Total logs now: {ThreatLog.objects.count()}")
