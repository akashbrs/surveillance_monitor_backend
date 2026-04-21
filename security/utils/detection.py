import re
from django.core.cache import cache

class AttackDetector:
    # Patterns
    SQLI_PATTERNS = [
        r"(?i)'.*OR.*=.*",
        r"(?i)UNION.*SELECT",
        r"(?i)--",
        r"(?i);",
        r"(?i)DROP.*TABLE",
    ]
    
    XSS_PATTERNS = [
        r"(?i)<script.*?>",
        r"(?i)javascript:",
        r"(?i)onerror=",
        r"(?i)alert\(.*?\)",
        r"(?i)<img.*?src=.*?>",
    ]

    @staticmethod
    def get_client_ip(request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    @staticmethod
    def detect_sqli(payload):
        if not payload: return False
        for pattern in AttackDetector.SQLI_PATTERNS:
            if re.search(pattern, str(payload)):
                return True
        return False

    @staticmethod
    def detect_xss(payload):
        if not payload: return False
        for pattern in AttackDetector.XSS_PATTERNS:
            if re.search(pattern, str(payload)):
                return True
        return False

    @staticmethod
    def check_brute_force(ip, is_failed_login):
        if not is_failed_login:
            return False
        
        cache_key = f"brute_force_{ip}"
        attempts = cache.get(cache_key, 0)
        attempts += 1
        cache.set(cache_key, attempts, timeout=300) # 5 minutes window
        
        if attempts >= 5: # Threshold
            return True
        return False

    @staticmethod
    def check_ddos(ip):
        cache_key = f"ddos_{ip}"
        requests_count = cache.get(cache_key, 0)
        requests_count += 1
        cache.set(cache_key, requests_count, timeout=60) # 1 minute window
        
        if requests_count > 100: # Threshold: > 100 requests per minute
            return True
        return False

    @staticmethod
    def get_severity(attack_type):
        severity_map = {
            'SQLI': 'Critical',
            'XSS': 'High',
            'DDOS': 'Critical',
            'BRUTE': 'High'
        }
        return severity_map.get(attack_type, 'Medium')
