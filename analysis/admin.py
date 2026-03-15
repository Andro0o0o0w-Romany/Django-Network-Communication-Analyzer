from django.contrib import admin
from .models import AnalysisResult

@admin.register(AnalysisResult)
class AnalysisResultAdmin(admin.ModelAdmin):
    list_display = ['topology', 'ruleset', 'risk_score', 'created_at']
    list_filter = ['topology', 'ruleset']
