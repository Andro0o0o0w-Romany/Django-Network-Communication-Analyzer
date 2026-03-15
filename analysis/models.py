from django.db import models


class AnalysisResult(models.Model):
    topology = models.ForeignKey('network.NetworkTopology', on_delete=models.CASCADE, related_name='analyses')
    ruleset = models.ForeignKey('rules.RuleSet', on_delete=models.SET_NULL, null=True, blank=True, related_name='analyses')
    created_at = models.DateTimeField(auto_now_add=True)
    results_data = models.JSONField(default=dict)
    risk_score = models.FloatField(default=0)
    summary = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Analysis of {self.topology.name} at {self.created_at.strftime("%Y-%m-%d %H:%M")}'

    @property
    def risk_level(self):
        if self.risk_score >= 70:
            return 'critical'
        elif self.risk_score >= 40:
            return 'warning'
        elif self.risk_score >= 10:
            return 'moderate'
        return 'low'

    @property
    def risk_color(self):
        return {'critical': 'danger', 'warning': 'warning', 'moderate': 'info', 'low': 'success'}.get(self.risk_level, 'secondary')

    @property
    def failure_points_count(self):
        fp = self.results_data.get('failure_points', {})
        return len(fp.get('articulation_points', [])) + len(fp.get('bridges', []))

    @property
    def violations_count(self):
        return len(self.results_data.get('rule_violations', []))

    @property
    def suggestions_count(self):
        return len(self.results_data.get('device_suggestions', []))
