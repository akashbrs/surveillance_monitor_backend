from django.urls import path
from .views import ThreatLogView, AttackStatsView, AttackTypeView, TopIPView

urlpatterns = [
    # Main log endpoint (GET: List, POST: Receive)
    path('logs/', ThreatLogView.as_view(), name='logs'),

    # Other dashboard views
    path('stats/', AttackStatsView.as_view(), name='stats'),
    path('types/', AttackTypeView.as_view(), name='types'),
    path('top-ips/', TopIPView.as_view(), name='top_ips'),
]



