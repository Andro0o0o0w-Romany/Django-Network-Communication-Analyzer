import json
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

from .models import NetworkTopology, Node, Connection
from analysis.models import AnalysisResult
from rules.models import RuleSet


def dashboard(request):
    topologies = NetworkTopology.objects.all()
    recent_analyses = AnalysisResult.objects.select_related('topology')[:5]
    stats = {
        'total_networks': topologies.count(),
        'total_nodes': Node.objects.count(),
        'total_connections': Connection.objects.count(),
        'total_analyses': AnalysisResult.objects.count(),
    }
    return render(request, 'network/dashboard.html', {
        'topologies': topologies,
        'recent_analyses': recent_analyses,
        'stats': stats,
    })


def topology_list(request):
    topologies = NetworkTopology.objects.all()
    return render(request, 'network/topology_list.html', {'topologies': topologies})


def topology_create(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        if not name:
            messages.error(request, 'Network name is required.')
            return render(request, 'network/topology_form.html', {'action': 'Create'})
        topology = NetworkTopology.objects.create(name=name, description=description)
        messages.success(request, f'Network "{topology.name}" created successfully.')
        return redirect('network:topology_detail', pk=topology.pk)
    return render(request, 'network/topology_form.html', {'action': 'Create'})


def topology_edit(request, pk):
    topology = get_object_or_404(NetworkTopology, pk=pk)
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        if not name:
            messages.error(request, 'Network name is required.')
            return render(request, 'network/topology_form.html', {'topology': topology, 'action': 'Edit'})
        topology.name = name
        topology.description = description
        topology.save()
        messages.success(request, 'Network updated successfully.')
        return redirect('network:topology_detail', pk=topology.pk)
    return render(request, 'network/topology_form.html', {'topology': topology, 'action': 'Edit'})


def topology_detail(request, pk):
    topology = get_object_or_404(NetworkTopology, pk=pk)
    nodes = topology.nodes.all()
    connections = topology.connections.all()
    rulesets = RuleSet.objects.all()
    recent_analysis = topology.analyses.first()
    return render(request, 'network/topology_detail.html', {
        'topology': topology,
        'nodes': nodes,
        'connections': connections,
        'rulesets': rulesets,
        'recent_analysis': recent_analysis,
    })


def topology_delete(request, pk):
    topology = get_object_or_404(NetworkTopology, pk=pk)
    if request.method == 'POST':
        name = topology.name
        topology.delete()
        messages.success(request, f'Network "{name}" deleted.')
        return redirect('network:topology_list')
    return render(request, 'network/topology_confirm_delete.html', {'topology': topology})


# ---- Nodes ----

def node_create(request, topology_pk):
    topology = get_object_or_404(NetworkTopology, pk=topology_pk)
    if request.method == 'POST':
        try:
            node = Node.objects.create(
                topology=topology,
                name=request.POST['name'],
                node_type=request.POST['node_type'],
                capacity=float(request.POST.get('capacity', 1000)),
                processing_delay=float(request.POST.get('processing_delay', 1)),
                status=request.POST.get('status', 'active'),
                ip_address=request.POST.get('ip_address') or None,
                description=request.POST.get('description', ''),
                x_pos=float(request.POST.get('x_pos', 300)),
                y_pos=float(request.POST.get('y_pos', 300)),
            )
            messages.success(request, f'Node "{node.name}" added.')
        except Exception as e:
            messages.error(request, f'Error creating node: {e}')
        return redirect('network:topology_detail', pk=topology_pk)
    return render(request, 'network/node_form.html', {
        'topology': topology,
        'node_types': Node.NODE_TYPES,
        'status_choices': Node.STATUS_CHOICES,
        'action': 'Add',
    })


def node_edit(request, pk):
    node = get_object_or_404(Node, pk=pk)
    topology = node.topology
    if request.method == 'POST':
        try:
            node.name = request.POST['name']
            node.node_type = request.POST['node_type']
            node.capacity = float(request.POST.get('capacity', 1000))
            node.processing_delay = float(request.POST.get('processing_delay', 1))
            node.status = request.POST.get('status', 'active')
            node.ip_address = request.POST.get('ip_address') or None
            node.description = request.POST.get('description', '')
            node.save()
            messages.success(request, f'Node "{node.name}" updated.')
        except Exception as e:
            messages.error(request, f'Error updating node: {e}')
        return redirect('network:topology_detail', pk=topology.pk)
    return render(request, 'network/node_form.html', {
        'node': node,
        'topology': topology,
        'node_types': Node.NODE_TYPES,
        'status_choices': Node.STATUS_CHOICES,
        'action': 'Edit',
    })


def node_delete(request, pk):
    node = get_object_or_404(Node, pk=pk)
    topology_pk = node.topology.pk
    if request.method == 'POST':
        name = node.name
        node.delete()
        messages.success(request, f'Node "{name}" deleted.')
    return redirect('network:topology_detail', pk=topology_pk)


# ---- Connections ----

def connection_create(request, topology_pk):
    topology = get_object_or_404(NetworkTopology, pk=topology_pk)
    nodes = topology.nodes.filter(status__in=['active', 'degraded'])
    if request.method == 'POST':
        try:
            conn = Connection.objects.create(
                topology=topology,
                source_id=request.POST['source'],
                target_id=request.POST['target'],
                connection_type=request.POST.get('connection_type', 'ethernet'),
                bandwidth=float(request.POST.get('bandwidth', 1000)),
                latency=float(request.POST.get('latency', 1)),
                reliability=float(request.POST.get('reliability', 99.9)),
                distance=float(request.POST.get('distance', 100)),
                is_active=request.POST.get('is_active') == 'on',
                description=request.POST.get('description', ''),
            )
            messages.success(request, f'Connection {conn} added.')
        except Exception as e:
            messages.error(request, f'Error creating connection: {e}')
        return redirect('network:topology_detail', pk=topology_pk)
    return render(request, 'network/connection_form.html', {
        'topology': topology,
        'nodes': nodes,
        'connection_types': Connection.CONNECTION_TYPES,
        'action': 'Add',
    })


def connection_edit(request, pk):
    conn = get_object_or_404(Connection, pk=pk)
    topology = conn.topology
    nodes = topology.nodes.all()
    if request.method == 'POST':
        try:
            conn.source_id = request.POST['source']
            conn.target_id = request.POST['target']
            conn.connection_type = request.POST.get('connection_type', 'ethernet')
            conn.bandwidth = float(request.POST.get('bandwidth', 1000))
            conn.latency = float(request.POST.get('latency', 1))
            conn.reliability = float(request.POST.get('reliability', 99.9))
            conn.distance = float(request.POST.get('distance', 100))
            conn.is_active = request.POST.get('is_active') == 'on'
            conn.description = request.POST.get('description', '')
            conn.save()
            messages.success(request, 'Connection updated.')
        except Exception as e:
            messages.error(request, f'Error updating connection: {e}')
        return redirect('network:topology_detail', pk=topology.pk)
    return render(request, 'network/connection_form.html', {
        'conn': conn,
        'topology': topology,
        'nodes': nodes,
        'connection_types': Connection.CONNECTION_TYPES,
        'action': 'Edit',
    })


def connection_delete(request, pk):
    conn = get_object_or_404(Connection, pk=pk)
    topology_pk = conn.topology.pk
    if request.method == 'POST':
        conn.delete()
        messages.success(request, 'Connection deleted.')
    return redirect('network:topology_detail', pk=topology_pk)


# ---- API ----

def graph_data(request, pk):
    topology = get_object_or_404(NetworkTopology, pk=pk)
    nodes_data = []
    for node in topology.nodes.all():
        nodes_data.append({
            'id': node.id,
            'label': node.name,
            'title': f'{node.get_node_type_display()}\nStatus: {node.get_status_display()}\nCapacity: {node.capacity} Mbps',
            'x': node.x_pos,
            'y': node.y_pos,
            'color': {'background': node.color, 'border': '#1f2937'},
            'node_type': node.node_type,
            'status': node.status,
            'font': {'color': '#ffffff', 'size': 12},
            'borderWidth': 2,
            'size': 25,
        })

    edges_data = []
    for conn in topology.connections.filter(is_active=True):
        edges_data.append({
            'id': conn.id,
            'from': conn.source_id,
            'to': conn.target_id,
            'label': f'{conn.bandwidth}M',
            'title': f'{conn.get_connection_type_display()}\nBW: {conn.bandwidth}Mbps\nLatency: {conn.latency}ms\nReliability: {conn.reliability}%',
            'color': {'color': '#6b7280', 'highlight': '#3b82f6'},
            'font': {'color': '#9ca3af', 'size': 10},
            'smooth': {'type': 'curvedCW', 'roundness': 0.1},
        })

    return JsonResponse({'nodes': nodes_data, 'edges': edges_data})


@require_POST
def save_positions(request, pk):
    topology = get_object_or_404(NetworkTopology, pk=pk)
    try:
        data = json.loads(request.body)
        for item in data.get('positions', []):
            Node.objects.filter(id=item['id'], topology=topology).update(
                x_pos=item['x'], y_pos=item['y']
            )
        return JsonResponse({'status': 'ok'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
