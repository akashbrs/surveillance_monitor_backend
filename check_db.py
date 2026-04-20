import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from security.models import ThreatLog, BlockedIP

print(f"Total ThreatLogs: {ThreatLog.objects.count()}")
print(f"Total BlockedIPs: {BlockedIP.objects.count()}")

latest_logs = ThreatLog.objects.all().order_by("-timestamp")[:5]
for log in latest_logs:
    print(f"Log: {log.target} | {log.ip} | {log.attack_type} | {log.timestamp}")
