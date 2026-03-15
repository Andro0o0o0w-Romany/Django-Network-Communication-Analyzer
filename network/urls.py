from django.urls import path
from . import views

app_name = 'network'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('topologies/', views.topology_list, name='topology_list'),
    path('topologies/create/', views.topology_create, name='topology_create'),
    path('topologies/<int:pk>/', views.topology_detail, name='topology_detail'),
    path('topologies/<int:pk>/edit/', views.topology_edit, name='topology_edit'),
    path('topologies/<int:pk>/delete/', views.topology_delete, name='topology_delete'),

    # Nodes
    path('topologies/<int:topology_pk>/nodes/create/', views.node_create, name='node_create'),
    path('nodes/<int:pk>/edit/', views.node_edit, name='node_edit'),
    path('nodes/<int:pk>/delete/', views.node_delete, name='node_delete'),

    # Connections
    path('topologies/<int:topology_pk>/connections/create/', views.connection_create, name='connection_create'),
    path('connections/<int:pk>/edit/', views.connection_edit, name='connection_edit'),
    path('connections/<int:pk>/delete/', views.connection_delete, name='connection_delete'),

    # API endpoints for vis.js
    path('topologies/<int:pk>/graph-data/', views.graph_data, name='graph_data'),
    path('topologies/<int:pk>/save-positions/', views.save_positions, name='save_positions'),
]
