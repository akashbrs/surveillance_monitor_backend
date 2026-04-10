import os
import django
from django.urls import get_resolver

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

resolver = get_resolver()
def list_urls(patterns, prefix=''):
    for p in patterns:
        if hasattr(p, 'url_patterns'):
            list_urls(p.url_patterns, prefix + str(p.pattern))
        else:
            print(prefix + str(p.pattern))

list_urls(resolver.url_patterns)
