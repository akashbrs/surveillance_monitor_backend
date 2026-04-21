from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import AttackLog, BlockedIP
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta


class AttackLogView(APIView):
    """
    GET → Return all attacks (ALL types)
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        logs = AttackLog.objects.all().order_by("-timestamp")
        data = [
            {
                "attack_type": log.get_attack_type_display(),
                "type_code": log.attack_type,
                "ip_address": log.ip_address,
                "target": log.target,
                "timestamp": log.timestamp.isoformat(),
                "severity": log.severity,
                "status": log.status,
                "payload": log.payload
            }
            for log in logs
        ]
        return Response({"data": data})


class AttackStatsView(APIView):
    """
    GET → return: { total_attacks, sqli_count, xss_count, ddos_count, brute_force_count }
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        total = AttackLog.objects.count()
        counts = AttackLog.objects.values('attack_type').annotate(count=Count('attack_type'))
        
        stats = {
            "total_attacks": total,
            "sqli_count": 0,
            "xss_count": 0,
            "ddos_count": 0,
            "brute_force_count": 0
        }
        
        for item in counts:
            if item['attack_type'] == 'SQLI': stats["sqli_count"] = item['count']
            elif item['attack_type'] == 'XSS': stats["xss_count"] = item['count']
            elif item['attack_type'] == 'DDOS': stats["ddos_count"] = item['count']
            elif item['attack_type'] == 'BRUTE': stats["brute_force_count"] = item['count']
            
        return Response({"data": stats})


class RecentAttacksView(APIView):
    """
    GET → latest attack logs
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        logs = AttackLog.objects.all().order_by("-timestamp")[:10]
        data = [
            {
                "attack_type": log.get_attack_type_display(),
                "ip_address": log.ip_address,
                "target": log.target,
                "timestamp": log.timestamp.isoformat(),
                "severity": log.severity,
                "status": log.status
            }
            for log in logs
        ]
        return Response({"data": data})