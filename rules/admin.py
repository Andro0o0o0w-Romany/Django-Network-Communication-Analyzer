from django.contrib import admin
from .models import RuleSet, Rule

@admin.register(RuleSet)
class RuleSetAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_default', 'active_rules_count', 'updated_at']

@admin.register(Rule)
class RuleAdmin(admin.ModelAdmin):
    list_display = ['name', 'rule_type', 'threshold', 'severity', 'is_enabled', 'ruleset']
    list_filter = ['severity', 'is_enabled', 'ruleset']
