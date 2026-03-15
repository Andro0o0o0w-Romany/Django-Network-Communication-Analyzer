from django.db import models


class RuleSet(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_default', 'name']

    def __str__(self):
        return self.name

    def active_rules_count(self):
        return self.rules.filter(is_enabled=True).count()


class Rule(models.Model):
    RULE_TYPES = [
        ('max_latency', 'Maximum Link Latency'),
        ('min_bandwidth', 'Minimum Link Bandwidth'),
        ('min_reliability', 'Minimum Link Reliability'),
        ('max_distance', 'Maximum Link Distance'),
        ('min_redundancy', 'Minimum Redundant Paths'),
        ('max_connections', 'Maximum Node Connections'),
        ('min_connections', 'Minimum Node Connections'),
        ('max_hop_count', 'Maximum Hop Count'),
        ('max_node_load', 'Maximum Node Load Factor'),
        ('min_path_diversity', 'Minimum Path Diversity'),
        ('critical_backup', 'Critical Nodes Require Backup'),
        ('max_single_bandwidth', 'Maximum Single Connection Bandwidth'),
    ]
    SEVERITY_CHOICES = [
        ('info', 'Info'),
        ('warning', 'Warning'),
        ('critical', 'Critical'),
    ]

    ruleset = models.ForeignKey(RuleSet, on_delete=models.CASCADE, related_name='rules')
    name = models.CharField(max_length=200)
    rule_type = models.CharField(max_length=50, choices=RULE_TYPES)
    threshold = models.FloatField(help_text='Numeric threshold value for this rule')
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default='warning')
    is_enabled = models.BooleanField(default=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-severity', 'name']

    def __str__(self):
        return f'{self.name} ({self.get_severity_display()})'

    @property
    def severity_color(self):
        return {'info': 'info', 'warning': 'warning', 'critical': 'danger'}.get(self.severity, 'secondary')
