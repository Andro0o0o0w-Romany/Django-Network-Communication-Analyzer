from django.db import models


class NetworkTopology(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']
        verbose_name_plural = 'Network Topologies'

    def __str__(self):
        return self.name

    def node_count(self):
        return self.nodes.count()

    def connection_count(self):
        return self.connections.count()


class Node(models.Model):
    NODE_TYPES = [
        ('router', 'Router'),
        ('switch', 'Switch'),
        ('hub', 'Hub'),
        ('endpoint', 'Endpoint'),
        ('repeater', 'Repeater'),
        ('firewall', 'Firewall'),
        ('server', 'Server'),
        ('access_point', 'Access Point'),
        ('gateway', 'Gateway'),
        ('load_balancer', 'Load Balancer'),
    ]
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('degraded', 'Degraded'),
        ('failed', 'Failed'),
    ]

    topology = models.ForeignKey(NetworkTopology, on_delete=models.CASCADE, related_name='nodes')
    name = models.CharField(max_length=100)
    node_type = models.CharField(max_length=20, choices=NODE_TYPES, default='router')
    x_pos = models.FloatField(default=300)
    y_pos = models.FloatField(default=300)
    capacity = models.FloatField(default=1000, help_text='Throughput capacity in Mbps')
    processing_delay = models.FloatField(default=1, help_text='Processing delay in ms')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f'{self.name} ({self.get_node_type_display()})'

    @property
    def degree(self):
        return self.outgoing.filter(is_active=True).count() + self.incoming.filter(is_active=True).count()

    @property
    def color(self):
        colors = {
            'router': '#3b82f6',
            'switch': '#10b981',
            'hub': '#f59e0b',
            'endpoint': '#8b5cf6',
            'repeater': '#06b6d4',
            'firewall': '#ef4444',
            'server': '#6366f1',
            'access_point': '#14b8a6',
            'gateway': '#f97316',
            'load_balancer': '#ec4899',
        }
        return colors.get(self.node_type, '#6b7280')

    @property
    def icon(self):
        icons = {
            'router': 'fa-network-wired',
            'switch': 'fa-shuffle',
            'hub': 'fa-circle-nodes',
            'endpoint': 'fa-desktop',
            'repeater': 'fa-tower-broadcast',
            'firewall': 'fa-shield-halved',
            'server': 'fa-server',
            'access_point': 'fa-wifi',
            'gateway': 'fa-door-open',
            'load_balancer': 'fa-scale-balanced',
        }
        return icons.get(self.node_type, 'fa-circle')


class Connection(models.Model):
    CONNECTION_TYPES = [
        ('fiber', 'Fiber Optic'),
        ('ethernet', 'Ethernet'),
        ('wifi', 'Wi-Fi'),
        ('coaxial', 'Coaxial'),
        ('microwave', 'Microwave'),
        ('satellite', 'Satellite'),
    ]

    topology = models.ForeignKey(NetworkTopology, on_delete=models.CASCADE, related_name='connections')
    source = models.ForeignKey(Node, on_delete=models.CASCADE, related_name='outgoing')
    target = models.ForeignKey(Node, on_delete=models.CASCADE, related_name='incoming')
    connection_type = models.CharField(max_length=20, choices=CONNECTION_TYPES, default='ethernet')
    bandwidth = models.FloatField(default=1000, help_text='Bandwidth in Mbps')
    latency = models.FloatField(default=1, help_text='Latency in ms')
    reliability = models.FloatField(default=99.9, help_text='Reliability percentage (0-100)')
    distance = models.FloatField(default=100, help_text='Distance in meters')
    is_active = models.BooleanField(default=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['source__name', 'target__name']

    def __str__(self):
        return f'{self.source.name} -> {self.target.name}'

    @property
    def weight(self):
        return self.latency + (1 / max(self.bandwidth, 0.001)) * 100 + (100 - self.reliability)
