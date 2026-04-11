from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Count
from rest_framework.permissions import AllowAny, IsAuthenticated

from .models import ThreatLog, BlockedIP


class ThreatLogView(APIView):
    """
    GET → Dashboard logs
    POST → Receive logs from other services
    """

    def get_permissions(self):
        if self.request.method == 'POST':
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_app_name(self, target):
        if target == "electronics":
            return "Electronics App"
        elif target == "fashion":
            return "Fashion App"
        elif target == "organization":
            return "Organization App"
        return "Unknown"

    # ✅ GET → for dashboard
    def get(self, request):
        logs = ThreatLog.objects.all().order_by("-timestamp")

        data = [
            {
                "id": str(log.id),
                "ip": log.ip,
                "attackType": log.attack_type,  # ✅ Frontend expects camelCase
                "payload": log.payload,
                "severity": self.get_severity(log.attack_type),
                "timestamp": log.timestamp.isoformat(),  
                "status": "Active" if not log.resolved else "Resolved",  
                "app": self.get_app_name(log.target),
                "target": log.target
            }
            for log in logs
        ]

        return Response({"data": data})

    # ✅ POST → from electronics backend
    def post(self, request):
        data = request.data

        print(f"--- [DEBUG: New Threat Log Received | Target: {data.get('target')} | Type: {data.get('attack_type')} | IP: {data.get('ip')} ] ---")
        ThreatLog.objects.create(
            target=data.get("target", "unknown"),
            ip=data.get("ip"),
            attack_type=data.get("attack_type"),
            endpoint=data.get("endpoint", "unknown"),  # ✅ FIXED
            payload=data.get("payload", ""),
            user_agent=data.get("user_agent", "")
        )

        return Response({"message": "Log received"})

    # 🔥 Severity logic (Aligned with frontend severityColor helper)
    def get_severity(self, attack_type):
        return {
            "SQL Injection": "Critical",
            "SQLi": "Critical",
            "XSS": "High",
            "DDOS": "Critical",
            "DDoS": "Critical",
            "Brute Force": "High",
            "Bruteforce": "High"
        }.get(attack_type, "Low")
    

    

from django.utils import timezone
from datetime import timedelta

# 📊 STATS
class AttackStatsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        total_logs = ThreatLog.objects.count()
        blocked_ips = BlockedIP.objects.count()
        active = ThreatLog.objects.filter(resolved=False, ignored=False).count()

        # Generate Real Activity Timeline for last 24 hours
        now = timezone.now()
        timeline = []
        for i in range(12, -1, -1): # Last 12 intervals of 2 hours for cleaner chart
            h = i * 2
            start = now - timedelta(hours=h+2)
            end = now - timedelta(hours=h)
            count = ThreatLog.objects.filter(timestamp__range=(start, end)).count()
            timeline.append({
                "time": end.strftime("%H:00"),
                "attacks": count
            })

        return Response({
            "data": {
                "totalLogs": total_logs,
                "totalAttacks": total_logs,
                "activeThreats": active,
                "blockedIPs": blocked_ips,
                "activityTimeline": timeline
            }
        })


# 📈 TYPES
class AttackTypeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        types = ThreatLog.objects.values("attack_type").annotate(count=Count("attack_type"))

        return Response({
            item["attack_type"]: item["count"] for item in types
        })


# 🌍 TOP IPs
class TopIPView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        ips = (
            ThreatLog.objects.values("ip")
            .annotate(attack_count=Count("ip"))
            .order_by("-attack_count")[:5]
        )

        return Response(list(ips))