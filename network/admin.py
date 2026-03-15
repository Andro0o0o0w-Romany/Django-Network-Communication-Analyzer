from django.contrib import admin
from .models import NetworkTopology, Node, Connection

@admin.register(NetworkTopology)
class NetworkTopologyAdmin(admin.ModelAdmin):
    list_display = ['name', 'node_count', 'connection_count', 'updated_at']
    search_fields = ['name']

@admin.register(Node)
class NodeAdmin(admin.ModelAdmin):
    list_display = ['name', 'node_type', 'status', 'topology', 'capacity']
    list_filter = ['node_type', 'status', 'topology']

@admin.register(Connection)
class ConnectionAdmin(admin.ModelAdmin):
    list_display = ['source', 'target', 'connection_type', 'bandwidth', 'latency', 'is_active']
    list_filter = ['connection_type', 'is_active', 'topology']
