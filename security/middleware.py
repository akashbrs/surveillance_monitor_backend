import json
from .utils.detection import AttackDetector
from .models import AttackLog, BlockedIP

class ThreatDetectionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        ip = AttackDetector.get_client_ip(request)
        
        # Check if IP is already blocked
        if BlockedIP.objects.filter(ip_address=ip).exists():
            from django.http import HttpResponseForbidden
            return HttpResponseForbidden("Your IP has been blocked due to suspicious activity.")

        # 1. DDoS Detection (on every request)
        if AttackDetector.check_ddos(ip):
            self.log_attack(request, 'DDOS', ip, "DDoS attack detected: High request frequency", severity='Critical', status='Detected')

        # 2. SQLi and XSS Detection
        payload = ""
        if request.method in ['POST', 'PUT', 'PATCH']:
            try:
                if request.content_type == 'application/json':
                    payload = json.dumps(request.data) if hasattr(request, 'data') else request.body.decode('utf-8')
                else:
                    payload = str(request.POST.dict())
            except:
                payload = str(request.body)

        if AttackDetector.detect_sqli(payload) or AttackDetector.detect_sqli(request.GET.dict()):
            self.log_attack(request, 'SQLI', ip, payload)

        if AttackDetector.detect_xss(payload) or AttackDetector.detect_xss(request.GET.dict()):
            self.log_attack(request, 'XSS', ip, payload)

        # 3. Brute Force Detection
        # (This is usually triggered on the login view, but we can catch login attempts here)
        if request.path == '/api/auth/login/' and request.method == 'POST':
            # We don't know yet if it failed, but we can wrap the response
            response = self.get_response(request)
            if response.status_code == 401:
                if AttackDetector.check_brute_force(ip, True):
                    self.log_attack(request, 'BRUTE', ip, "Multiple failed login attempts", severity='High', status='Detected')
            return response

        response = self.get_response(request)
        return response

    def log_attack(self, request, attack_type, ip, payload, severity=None, status='Detected'):
        # Determine target from URL or headers
        target = "Unknown"
        host = request.get_host().lower()
        if 'electron' in host:
            target = "Electron Website"
        elif 'veloura' in host:
            target = "Veloura Website"
        else:
            # Fallback to some logic to determine target
            target = "Core API"

        AttackLog.objects.create(
            attack_type=attack_type,
            ip_address=ip,
            target=target,
            severity=severity or AttackDetector.get_severity(attack_type),
            status=status,
            payload=str(payload)[:1000] # Limit payload size
        )
