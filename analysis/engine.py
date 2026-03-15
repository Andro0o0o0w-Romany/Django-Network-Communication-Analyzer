import networkx as nx
import math


class NetworkAnalyzer:
    def __init__(self, topology, ruleset=None):
        self.topology = topology
        self.ruleset = ruleset
        self.G = self._build_graph()
        self.node_map = {}  # id -> node object
        self.conn_map = {}  # (src_id, tgt_id) -> connection object
        self._build_maps()

    def _build_maps(self):
        for node in self.topology.nodes.all():
            self.node_map[node.id] = node
        for conn in self.topology.connections.all():
            self.conn_map[(conn.source_id, conn.target_id)] = conn
            self.conn_map[(conn.target_id, conn.source_id)] = conn

    def _build_graph(self):
        G = nx.Graph()
        for node in self.topology.nodes.filter(status__in=['active', 'degraded']):
            G.add_node(node.id,
                       name=node.name,
                       node_type=node.node_type,
                       capacity=node.capacity,
                       status=node.status,
                       processing_delay=node.processing_delay)
        for conn in self.topology.connections.filter(is_active=True):
            if conn.source_id in G.nodes and conn.target_id in G.nodes:
                G.add_edge(conn.source_id, conn.target_id,
                           bandwidth=conn.bandwidth,
                           latency=conn.latency,
                           reliability=conn.reliability,
                           distance=conn.distance,
                           weight=conn.latency,
                           connection_id=conn.id)
        return G

    # -------------------------------------------------------------------------
    # FAILURE POINT ANALYSIS
    # -------------------------------------------------------------------------
    def find_failure_points(self):
        if self.G.number_of_nodes() == 0:
            return {'articulation_points': [], 'bridges': [], 'is_connected': True, 'components': 1, 'isolated_nodes': []}

        connected_components = list(nx.connected_components(self.G))
        is_connected = len(connected_components) == 1

        articulation_points = []
        if is_connected:
            for node_id in nx.articulation_points(self.G):
                node_data = self.G.nodes[node_id]
                degree = self.G.degree(node_id)
                # Calculate impact: how many nodes become disconnected if removed
                G_copy = self.G.copy()
                G_copy.remove_node(node_id)
                components_after = list(nx.connected_components(G_copy))
                max_isolated = max((len(c) for c in components_after), default=0)
                articulation_points.append({
                    'node_id': node_id,
                    'name': node_data['name'],
                    'node_type': node_data['node_type'],
                    'degree': degree,
                    'criticality': 'critical' if max_isolated > 3 else ('high' if max_isolated > 1 else 'medium'),
                    'nodes_isolated': max_isolated,
                    'components_after_removal': len(components_after),
                    'reason': f'Removing this node splits the network into {len(components_after)} disconnected segment(s), isolating up to {max_isolated} node(s)'
                })

        bridges = []
        if is_connected:
            for u, v in nx.bridges(self.G):
                edge_data = self.G.edges[u, v]
                G_copy = self.G.copy()
                G_copy.remove_edge(u, v)
                comps = list(nx.connected_components(G_copy))
                bridges.append({
                    'source_id': u,
                    'target_id': v,
                    'source_name': self.G.nodes[u]['name'],
                    'target_name': self.G.nodes[v]['name'],
                    'latency': edge_data.get('latency', 0),
                    'bandwidth': edge_data.get('bandwidth', 0),
                    'components_after': len(comps),
                    'reason': f'Removing this link disconnects the network into {len(comps)} segment(s)'
                })

        isolated_nodes = [
            {'node_id': n, 'name': self.G.nodes[n]['name'], 'node_type': self.G.nodes[n]['node_type']}
            for n in self.G.nodes() if self.G.degree(n) == 0
        ]

        return {
            'articulation_points': articulation_points,
            'bridges': bridges,
            'is_connected': is_connected,
            'components': len(connected_components),
            'isolated_nodes': isolated_nodes,
        }

    # -------------------------------------------------------------------------
    # OPTIMAL ROUTING
    # -------------------------------------------------------------------------
    def find_optimal_routes(self):
        routes = []
        nodes = list(self.G.nodes())

        for i, src in enumerate(nodes):
            for dst in nodes[i + 1:]:
                try:
                    path = nx.shortest_path(self.G, src, dst, weight='weight')
                    total_latency = sum(
                        self.G.edges[path[j], path[j + 1]].get('latency', 0)
                        for j in range(len(path) - 1)
                    )
                    min_bandwidth = min(
                        self.G.edges[path[j], path[j + 1]].get('bandwidth', 0)
                        for j in range(len(path) - 1)
                    ) if len(path) > 1 else 0

                    # Find up to 3 alternative paths
                    alt_paths = []
                    try:
                        all_simple = list(nx.all_simple_paths(self.G, src, dst, cutoff=8))
                        all_simple.sort(key=len)
                        for p in all_simple[1:4]:
                            alt_latency = sum(
                                self.G.edges[p[j], p[j + 1]].get('latency', 0)
                                for j in range(len(p) - 1)
                            )
                            alt_paths.append({
                                'path_ids': p,
                                'path_names': [self.G.nodes[n]['name'] for n in p],
                                'hops': len(p) - 1,
                                'total_latency': round(alt_latency, 2),
                            })
                    except Exception:
                        pass

                    routes.append({
                        'source_id': src,
                        'target_id': dst,
                        'source_name': self.G.nodes[src]['name'],
                        'target_name': self.G.nodes[dst]['name'],
                        'optimal_path_ids': path,
                        'optimal_path_names': [self.G.nodes[n]['name'] for n in path],
                        'hop_count': len(path) - 1,
                        'total_latency': round(total_latency, 2),
                        'bottleneck_bandwidth': round(min_bandwidth, 2),
                        'alternative_paths': alt_paths,
                        'path_diversity': len(alt_paths) + 1,
                    })
                except nx.NetworkXNoPath:
                    routes.append({
                        'source_id': src,
                        'target_id': dst,
                        'source_name': self.G.nodes[src]['name'],
                        'target_name': self.G.nodes[dst]['name'],
                        'optimal_path_ids': None,
                        'error': 'No path exists between these nodes',
                        'hop_count': None,
                        'total_latency': None,
                        'bottleneck_bandwidth': None,
                        'alternative_paths': [],
                        'path_diversity': 0,
                    })
        return routes

    # -------------------------------------------------------------------------
    # DEVICE PLACEMENT SUGGESTIONS
    # -------------------------------------------------------------------------
    def suggest_device_placements(self):
        suggestions = []

        # 1. Long connections need repeaters
        for conn in self.topology.connections.filter(is_active=True):
            max_dist = {'fiber': 80000, 'ethernet': 100, 'wifi': 300,
                        'coaxial': 500, 'microwave': 50000, 'satellite': 999999}
            limit = max_dist.get(conn.connection_type, 500)
            if conn.distance > limit:
                ratio = conn.distance / limit
                suggestions.append({
                    'type': 'repeater',
                    'priority': 'critical' if ratio > 5 else ('high' if ratio > 2 else 'medium'),
                    'location': f'Midpoint of {conn.source.name} — {conn.target.name}',
                    'between_nodes': [conn.source.name, conn.target.name],
                    'reason': f'{conn.get_connection_type_display()} link distance {conn.distance}m exceeds recommended {limit}m maximum',
                    'details': f'Consider placing {math.ceil(ratio) - 1} repeater(s) along this link',
                })

        # 2. High-degree nodes (potential bottlenecks) need load balancers
        for node_id in self.G.nodes():
            degree = self.G.degree(node_id)
            node = self.node_map.get(node_id)
            if node and degree >= 6:
                suggestions.append({
                    'type': 'load_balancer',
                    'priority': 'high' if degree >= 8 else 'medium',
                    'location': f'Near {node.name}',
                    'near_node': node.name,
                    'reason': f'{node.name} has {degree} connections and may become a bottleneck',
                    'details': f'Deploy a load balancer adjacent to {node.name} to distribute traffic',
                })

        # 3. Articulation points need backup/redundant nodes
        if self.G.number_of_nodes() > 0 and nx.is_connected(self.G):
            for ap_id in nx.articulation_points(self.G):
                node = self.node_map.get(ap_id)
                if node:
                    suggestions.append({
                        'type': 'redundant_node',
                        'priority': 'critical',
                        'location': f'Adjacent to {node.name}',
                        'near_node': node.name,
                        'reason': f'{node.name} is a single point of failure (articulation point)',
                        'details': f'Deploy a redundant {node.get_node_type_display()} to provide failover capability',
                    })

        # 4. Low-reliability links need redundant paths
        for conn in self.topology.connections.filter(is_active=True, reliability__lt=95):
            suggestions.append({
                'type': 'redundant_link',
                'priority': 'high' if conn.reliability < 90 else 'medium',
                'location': f'{conn.source.name} — {conn.target.name}',
                'between_nodes': [conn.source.name, conn.target.name],
                'reason': f'Link reliability {conn.reliability}% is below recommended 95%',
                'details': 'Add a parallel redundant link or switch to higher-reliability medium',
            })

        # 5. Nodes with no connections
        for node_id in self.G.nodes():
            if self.G.degree(node_id) == 0:
                node = self.node_map.get(node_id)
                if node:
                    suggestions.append({
                        'type': 'connection',
                        'priority': 'high',
                        'location': f'From {node.name}',
                        'near_node': node.name,
                        'reason': f'{node.name} is isolated with no connections',
                        'details': 'Connect this node to the network',
                    })

        # Sort by priority
        priority_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
        suggestions.sort(key=lambda x: priority_order.get(x['priority'], 4))
        return suggestions

    # -------------------------------------------------------------------------
    # RULE EVALUATION
    # -------------------------------------------------------------------------
    def evaluate_rules(self):
        if not self.ruleset:
            return []

        violations = []
        rules = self.ruleset.rules.filter(is_enabled=True)

        for rule in rules:
            rt = rule.rule_type
            th = rule.threshold

            if rt == 'max_latency':
                for conn in self.topology.connections.filter(is_active=True):
                    if conn.latency > th:
                        violations.append({
                            'rule': rule.name,
                            'rule_type': rt,
                            'severity': rule.severity,
                            'message': f'Link {conn.source.name}→{conn.target.name}: latency {conn.latency}ms exceeds max {th}ms',
                            'affected_element': str(conn),
                        })

            elif rt == 'min_bandwidth':
                for conn in self.topology.connections.filter(is_active=True):
                    if conn.bandwidth < th:
                        violations.append({
                            'rule': rule.name,
                            'rule_type': rt,
                            'severity': rule.severity,
                            'message': f'Link {conn.source.name}→{conn.target.name}: bandwidth {conn.bandwidth}Mbps below minimum {th}Mbps',
                            'affected_element': str(conn),
                        })

            elif rt == 'min_reliability':
                for conn in self.topology.connections.filter(is_active=True):
                    if conn.reliability < th:
                        violations.append({
                            'rule': rule.name,
                            'rule_type': rt,
                            'severity': rule.severity,
                            'message': f'Link {conn.source.name}→{conn.target.name}: reliability {conn.reliability}% below minimum {th}%',
                            'affected_element': str(conn),
                        })

            elif rt == 'max_distance':
                for conn in self.topology.connections.filter(is_active=True):
                    if conn.distance > th:
                        violations.append({
                            'rule': rule.name,
                            'rule_type': rt,
                            'severity': rule.severity,
                            'message': f'Link {conn.source.name}→{conn.target.name}: distance {conn.distance}m exceeds max {th}m',
                            'affected_element': str(conn),
                        })

            elif rt == 'min_redundancy':
                nodes = list(self.G.nodes())
                insufficient = []
                for i, src in enumerate(nodes):
                    for dst in nodes[i + 1:]:
                        try:
                            paths = list(nx.all_simple_paths(self.G, src, dst, cutoff=10))
                            if len(paths) < th:
                                insufficient.append(f'{self.G.nodes[src]["name"]}↔{self.G.nodes[dst]["name"]} ({len(paths)} path(s))')
                        except Exception:
                            pass
                if insufficient:
                    violations.append({
                        'rule': rule.name,
                        'rule_type': rt,
                        'severity': rule.severity,
                        'message': f'{len(insufficient)} node pair(s) have fewer than {int(th)} redundant paths: {", ".join(insufficient[:3])}{"..." if len(insufficient) > 3 else ""}',
                        'affected_element': 'Multiple paths',
                    })

            elif rt == 'max_connections':
                for node_id in self.G.nodes():
                    degree = self.G.degree(node_id)
                    if degree > th:
                        violations.append({
                            'rule': rule.name,
                            'rule_type': rt,
                            'severity': rule.severity,
                            'message': f'Node {self.G.nodes[node_id]["name"]}: {degree} connections exceeds max {int(th)}',
                            'affected_element': self.G.nodes[node_id]['name'],
                        })

            elif rt == 'min_connections':
                for node_id in self.G.nodes():
                    degree = self.G.degree(node_id)
                    if degree < th:
                        violations.append({
                            'rule': rule.name,
                            'rule_type': rt,
                            'severity': rule.severity,
                            'message': f'Node {self.G.nodes[node_id]["name"]}: {degree} connection(s) below minimum {int(th)}',
                            'affected_element': self.G.nodes[node_id]['name'],
                        })

            elif rt == 'max_hop_count':
                nodes = list(self.G.nodes())
                violations_found = []
                for i, src in enumerate(nodes):
                    for dst in nodes[i + 1:]:
                        try:
                            path = nx.shortest_path(self.G, src, dst)
                            hops = len(path) - 1
                            if hops > th:
                                violations_found.append(f'{self.G.nodes[src]["name"]}↔{self.G.nodes[dst]["name"]} ({hops} hops)')
                        except nx.NetworkXNoPath:
                            pass
                if violations_found:
                    violations.append({
                        'rule': rule.name,
                        'rule_type': rt,
                        'severity': rule.severity,
                        'message': f'{len(violations_found)} pair(s) exceed {int(th)}-hop limit: {", ".join(violations_found[:3])}{"..." if len(violations_found) > 3 else ""}',
                        'affected_element': 'Multiple paths',
                    })

        return violations

    # -------------------------------------------------------------------------
    # NETWORK STATISTICS
    # -------------------------------------------------------------------------
    def get_network_stats(self):
        if self.G.number_of_nodes() == 0:
            return {'node_count': 0, 'edge_count': 0, 'density': 0,
                    'avg_degree': 0, 'is_connected': True, 'diameter': None,
                    'avg_clustering': 0, 'components': 0}
        degrees = [d for _, d in self.G.degree()]
        stats = {
            'node_count': self.G.number_of_nodes(),
            'edge_count': self.G.number_of_edges(),
            'density': round(nx.density(self.G), 4),
            'avg_degree': round(sum(degrees) / len(degrees), 2) if degrees else 0,
            'max_degree': max(degrees) if degrees else 0,
            'is_connected': nx.is_connected(self.G),
            'components': nx.number_connected_components(self.G),
            'avg_clustering': round(nx.average_clustering(self.G), 4),
        }
        if nx.is_connected(self.G):
            try:
                stats['diameter'] = nx.diameter(self.G)
                stats['radius'] = nx.radius(self.G)
                stats['avg_shortest_path'] = round(nx.average_shortest_path_length(self.G), 2)
            except Exception:
                stats['diameter'] = None
                stats['radius'] = None
                stats['avg_shortest_path'] = None
        else:
            stats['diameter'] = None
            stats['radius'] = None
            stats['avg_shortest_path'] = None
        return stats

    # -------------------------------------------------------------------------
    # FULL ANALYSIS
    # -------------------------------------------------------------------------
    def run_full_analysis(self):
        failure_points = self.find_failure_points()
        routing = self.find_optimal_routes()
        suggestions = self.suggest_device_placements()
        violations = self.evaluate_rules()
        stats = self.get_network_stats()

        # Compute risk score (0-100)
        risk = 0
        ap_count = len(failure_points.get('articulation_points', []))
        bridge_count = len(failure_points.get('bridges', []))
        critical_viol = sum(1 for v in violations if v['severity'] == 'critical')
        warning_viol = sum(1 for v in violations if v['severity'] == 'warning')
        critical_sugg = sum(1 for s in suggestions if s['priority'] == 'critical')

        risk += min(ap_count * 15, 40)
        risk += min(bridge_count * 10, 30)
        risk += min(critical_viol * 10, 20)
        risk += min(warning_viol * 3, 10)
        risk += min(critical_sugg * 5, 20)
        if not failure_points.get('is_connected', True):
            risk += 30
        risk = min(risk, 100)

        no_path_count = sum(1 for r in routing if r.get('error'))
        summary_parts = []
        if ap_count:
            summary_parts.append(f'{ap_count} critical failure point(s)')
        if bridge_count:
            summary_parts.append(f'{bridge_count} network bridge(s)')
        if no_path_count:
            summary_parts.append(f'{no_path_count} unreachable node pair(s)')
        if violations:
            summary_parts.append(f'{len(violations)} rule violation(s)')
        if not summary_parts:
            summary_parts.append('No critical issues detected')

        return {
            'failure_points': failure_points,
            'routing': routing,
            'device_suggestions': suggestions,
            'rule_violations': violations,
            'network_stats': stats,
            'risk_score': risk,
            'summary': '; '.join(summary_parts),
        }
