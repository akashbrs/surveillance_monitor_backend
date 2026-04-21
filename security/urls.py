from django.urls import path
from .views import AttackLogView, AttackStatsView, RecentAttacksView

urlpatterns = [
    # Full history
    path('', AttackLogView.as_view(), name='attacks'),
    
    # Stats
    path('stats/', AttackStatsView.as_view(), name='stats'),
    
    # Recent
    path('recent/', RecentAttacksView.as_view(), name='recent'),
]



