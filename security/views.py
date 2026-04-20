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
        target_lower = target.lower()
        if target_lower == "electronics" or target_lower == "electron":
            return "Electron App"
        elif target_lower == "fashion":
            return "Fashion App"
        elif target_lower == "organization":
            return "Organization App"
        elif target_lower == "veloura":
            return "Veloura App"
        return "Unknown"

    # ✅ GET → for dashboard
    def get(self, request):
        logs = ThreatLog.objects.all().order_by("-timestamp")

        data = [
            {
                "id": log.id,
                "ip": log.ip,
                "attackType": log.attack_type,
                "payload": log.payload,
                "severity": self.get_severity(log.attack_type),
                "timestamp": log.timestamp.isoformat(),  
                "status": "Active" if not log.resolved else "Resolved",  
                "resolved": log.resolved,
                "ignored": log.ignored,
                "app": self.get_app_name(log.target),
                "target": log.target,
                "endpoint": log.endpoint,
                "userAgent": log.user_agent
            }
            for log in logs
        ]

        return Response({"data": data})

    # ✅ POST → from other services (electronics, veloura, etc.)
    def post(self, request):
        data = request.data

        # Support both camelCase and snake_case for incoming logs
        target = data.get("target") or data.get("app") or "unknown"
        ip = data.get("ip") or data.get("attackerIp") or "unknown"
        attack_type = data.get("attack_type") or data.get("attackType") or "Unknown"
        endpoint = data.get("endpoint") or "unknown"
        payload = data.get("payload") or ""
        user_agent = data.get("user_agent") or data.get("userAgent") or ""

        print(f"--- [DEBUG: New Threat Log Received | Target: {target} | Type: {attack_type} | IP: {ip} ] ---")
        
        try:
            log = ThreatLog.objects.create(
                target=target,
                ip=ip,
                attack_type=attack_type,
                endpoint=endpoint,
                payload=payload,
                user_agent=user_agent
            )
            return Response({
                "message": "Log received", 
                "log_id": log.id
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            print(f"--- [ERROR: Failed to save log: {str(e)} ] ---")
            return Response({
                "message": "Failed to save log", 
                "error": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    # 🔥 Severity logic (Aligned with frontend severityColor helper)
    def get_severity(self, attack_type):
        at = str(attack_type).lower()
        if "sqli" in at or "injection" in at:
            return "Critical"
        if "xss" in at:
            return "High"
        if "ddos" in at:
            return "Critical"
        if "brute" in at:
            return "High"
        if "auth" in at or "login" in at:
            return "Medium"
        return "Low"
    

    

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