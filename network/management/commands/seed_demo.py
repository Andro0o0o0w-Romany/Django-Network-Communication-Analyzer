"""Management command to seed demo data."""
from django.core.management.base import BaseCommand
from network.models import NetworkTopology, Node, Connection
from rules.models import RuleSet, Rule


class Command(BaseCommand):
    help = 'Seeds demo network and ruleset data'

    def handle(self, *args, **options):
        self.stdout.write('Seeding demo data...')

        # ---- Default RuleSet ----
        rs, _ = RuleSet.objects.get_or_create(name='Production Standards', defaults={
            'description': 'Default production network rules',
            'is_default': True,
        })
        rules_data = [
            ('Max Link Latency', 'max_latency', 50, 'warning', 'Flag links with latency > 50ms'),
            ('Min Link Bandwidth', 'min_bandwidth', 100, 'warning', 'Flag links below 100 Mbps'),
            ('Min Link Reliability', 'min_reliability', 99, 'critical', 'Flag links below 99% reliability'),
            ('Max Link Distance', 'max_distance', 1000, 'warning', 'Flag links exceeding 1km'),
            ('Min Redundant Paths', 'min_redundancy', 2, 'critical', 'Every pair of nodes should have at least 2 paths'),
            ('Max Node Connections', 'max_connections', 8, 'warning', 'Flag nodes with more than 8 connections'),
            ('Min Node Connections', 'min_connections', 1, 'critical', 'All nodes must have at least 1 connection'),
            ('Max Hop Count', 'max_hop_count', 6, 'warning', 'Paths should not exceed 6 hops'),
        ]
        for name, rtype, threshold, severity, desc in rules_data:
            Rule.objects.get_or_create(ruleset=rs, name=name, defaults={
                'rule_type': rtype, 'threshold': threshold, 'severity': severity,
                'description': desc, 'is_enabled': True,
            })

        # ---- Campus Network Topology ----
        topo, _ = NetworkTopology.objects.get_or_create(name='Campus Network Alpha', defaults={
            'description': 'University campus communication network with core, distribution, and access layers'
        })

        if topo.nodes.count() == 0:
            nodes = {}
            node_data = [
                ('Core Router A', 'router', 100, 300, 'active', 10000, 0.5, '10.0.0.1'),
                ('Core Router B', 'router', 600, 300, 'active', 10000, 0.5, '10.0.0.2'),
                ('Dist Switch 1', 'switch', 200, 500, 'active', 1000, 1, '10.0.1.1'),
                ('Dist Switch 2', 'switch', 400, 500, 'active', 1000, 1, '10.0.1.2'),
                ('Dist Switch 3', 'switch', 300, 150, 'active', 1000, 1, '10.0.1.3'),
                ('Firewall GW', 'firewall', 350, 50, 'active', 2000, 2, '10.0.0.254'),
                ('Web Server', 'server', 150, 680, 'active', 1000, 2, '10.0.2.1'),
                ('DB Server', 'server', 450, 680, 'active', 1000, 2, '10.0.2.2'),
                ('AP Block A', 'access_point', 100, 680, 'active', 300, 3, '10.0.3.1'),
                ('AP Block B', 'access_point', 600, 680, 'active', 300, 3, '10.0.3.2'),
                ('Edge Router', 'gateway', 350, 350, 'active', 5000, 1, '10.0.0.10'),
                ('Repeater 1', 'repeater', 700, 500, 'active', 100, 1, None),
            ]
            for name, ntype, x, y, status, cap, delay, ip in node_data:
                n = Node.objects.create(
                    topology=topo, name=name, node_type=ntype,
                    x_pos=x, y_pos=y, status=status,
                    capacity=cap, processing_delay=delay, ip_address=ip,
                )
                nodes[name] = n

            conns = [
                ('Core Router A', 'Core Router B', 'fiber', 10000, 0.5, 99.99, 200),
                ('Core Router A', 'Dist Switch 1', 'fiber', 1000, 1, 99.9, 150),
                ('Core Router A', 'Dist Switch 3', 'fiber', 1000, 1, 99.9, 100),
                ('Core Router B', 'Dist Switch 2', 'fiber', 1000, 1, 99.9, 150),
                ('Core Router B', 'Dist Switch 3', 'fiber', 1000, 1, 99.9, 100),
                ('Core Router A', 'Firewall GW', 'fiber', 2000, 0.5, 99.9, 50),
                ('Core Router B', 'Edge Router', 'fiber', 5000, 0.5, 99.9, 80),
                ('Edge Router', 'Dist Switch 1', 'fiber', 1000, 1, 99.9, 120),
                ('Dist Switch 1', 'Web Server', 'ethernet', 1000, 1, 99.5, 80),
                ('Dist Switch 1', 'AP Block A', 'ethernet', 300, 2, 98, 50),
                ('Dist Switch 2', 'DB Server', 'ethernet', 1000, 1, 99.5, 80),
                ('Dist Switch 2', 'AP Block B', 'ethernet', 300, 2, 98, 50),
                ('Dist Switch 2', 'Repeater 1', 'ethernet', 100, 5, 95, 800),
                ('Repeater 1', 'AP Block B', 'ethernet', 100, 5, 93, 600),
            ]
            for src_name, tgt_name, ctype, bw, lat, rel, dist in conns:
                Connection.objects.create(
                    topology=topo,
                    source=nodes[src_name],
                    target=nodes[tgt_name],
                    connection_type=ctype,
                    bandwidth=bw, latency=lat, reliability=rel, distance=dist,
                    is_active=True,
                )

        # ---- Industrial Network (with deliberate failure points) ----
        topo2, _ = NetworkTopology.objects.get_or_create(name='Industrial Control Network', defaults={
            'description': 'SCADA network with intentional single points of failure for analysis demo'
        })

        if topo2.nodes.count() == 0:
            nodes2 = {}
            n2_data = [
                ('SCADA Master', 'server', 350, 100, 'active', 500, 2, '192.168.1.1'),
                ('Central Switch', 'switch', 350, 250, 'active', 1000, 1, '192.168.1.10'),
                ('PLC Zone A', 'endpoint', 150, 400, 'active', 100, 5, '192.168.2.1'),
                ('PLC Zone B', 'endpoint', 350, 450, 'active', 100, 5, '192.168.2.2'),
                ('PLC Zone C', 'endpoint', 550, 400, 'active', 100, 5, '192.168.2.3'),
                ('HMI Station 1', 'endpoint', 150, 600, 'active', 50, 10, '192.168.3.1'),
                ('HMI Station 2', 'endpoint', 550, 600, 'active', 50, 10, '192.168.3.2'),
                ('Historian', 'server', 600, 200, 'active', 200, 3, '192.168.1.5'),
            ]
            for name, ntype, x, y, status, cap, delay, ip in n2_data:
                n = Node.objects.create(
                    topology=topo2, name=name, node_type=ntype,
                    x_pos=x, y_pos=y, status=status,
                    capacity=cap, processing_delay=delay, ip_address=ip,
                )
                nodes2[name] = n

            conns2 = [
                ('SCADA Master', 'Central Switch', 'ethernet', 100, 2, 99, 50),
                ('Central Switch', 'PLC Zone A', 'ethernet', 100, 3, 97, 100),
                ('Central Switch', 'PLC Zone B', 'ethernet', 100, 3, 97, 80),
                ('Central Switch', 'PLC Zone C', 'ethernet', 100, 3, 97, 120),
                ('PLC Zone A', 'HMI Station 1', 'ethernet', 10, 10, 90, 200),
                ('PLC Zone C', 'HMI Station 2', 'ethernet', 10, 10, 90, 200),
                ('Central Switch', 'Historian', 'ethernet', 100, 2, 99, 60),
            ]
            for src_name, tgt_name, ctype, bw, lat, rel, dist in conns2:
                Connection.objects.create(
                    topology=topo2,
                    source=nodes2[src_name],
                    target=nodes2[tgt_name],
                    connection_type=ctype,
                    bandwidth=bw, latency=lat, reliability=rel, distance=dist,
                    is_active=True,
                )

        # ---- Data Center Spine-Leaf ----
        topo3, _ = NetworkTopology.objects.get_or_create(name='Data Center Spine-Leaf', defaults={
            'description': 'Modern spine-leaf data center topology with high redundancy and 40/100G links'
        })
        if topo3.nodes.count() == 0:
            n = {}
            nd = [
                # Spine layer
                ('Spine-1', 'router', 200, 100, 'active', 100000, 0.1, '172.16.0.1'),
                ('Spine-2', 'router', 500, 100, 'active', 100000, 0.1, '172.16.0.2'),
                ('Spine-3', 'router', 350, 50, 'active', 100000, 0.1, '172.16.0.3'),
                # Leaf layer
                ('Leaf-1', 'switch', 100, 280, 'active', 40000, 0.2, '172.16.1.1'),
                ('Leaf-2', 'switch', 220, 280, 'active', 40000, 0.2, '172.16.1.2'),
                ('Leaf-3', 'switch', 340, 280, 'active', 40000, 0.2, '172.16.1.3'),
                ('Leaf-4', 'switch', 460, 280, 'active', 40000, 0.2, '172.16.1.4'),
                ('Leaf-5', 'switch', 580, 280, 'active', 40000, 0.2, '172.16.1.5'),
                # Border/gateway
                ('Border LB', 'load_balancer', 350, 160, 'active', 40000, 0.5, '172.16.0.10'),
                ('Firewall Cluster', 'firewall', 350, 220, 'active', 20000, 1, '172.16.0.20'),
                # Compute racks
                ('Rack A1', 'server', 100, 420, 'active', 10000, 1, '10.1.1.1'),
                ('Rack A2', 'server', 180, 420, 'active', 10000, 1, '10.1.1.2'),
                ('Rack B1', 'server', 270, 420, 'active', 10000, 1, '10.1.2.1'),
                ('Rack B2', 'server', 350, 420, 'active', 10000, 1, '10.1.2.2'),
                ('Rack C1', 'server', 440, 420, 'active', 10000, 1, '10.1.3.1'),
                ('Rack C2', 'server', 520, 420, 'active', 10000, 1, '10.1.3.2'),
                ('Storage Node', 'server', 630, 420, 'degraded', 40000, 2, '10.1.9.1'),
            ]
            for name, ntype, x, y, status, cap, delay, ip in nd:
                n[name] = Node.objects.create(
                    topology=topo3, name=name, node_type=ntype,
                    x_pos=x, y_pos=y, status=status,
                    capacity=cap, processing_delay=delay, ip_address=ip,
                )
            c3 = [
                # Spine interconnects
                ('Spine-1', 'Spine-2', 'fiber', 100000, 0.1, 99.99, 30),
                ('Spine-2', 'Spine-3', 'fiber', 100000, 0.1, 99.99, 30),
                ('Spine-1', 'Spine-3', 'fiber', 100000, 0.1, 99.99, 30),
                # Border
                ('Spine-1', 'Border LB', 'fiber', 40000, 0.2, 99.99, 20),
                ('Spine-2', 'Border LB', 'fiber', 40000, 0.2, 99.99, 20),
                ('Border LB', 'Firewall Cluster', 'fiber', 40000, 0.3, 99.99, 10),
                # Spine to Leaf (every spine connects to every leaf)
                ('Spine-1', 'Leaf-1', 'fiber', 40000, 0.2, 99.99, 50),
                ('Spine-1', 'Leaf-2', 'fiber', 40000, 0.2, 99.99, 50),
                ('Spine-1', 'Leaf-3', 'fiber', 40000, 0.2, 99.99, 50),
                ('Spine-1', 'Leaf-4', 'fiber', 40000, 0.2, 99.99, 50),
                ('Spine-1', 'Leaf-5', 'fiber', 40000, 0.2, 99.99, 50),
                ('Spine-2', 'Leaf-1', 'fiber', 40000, 0.2, 99.99, 50),
                ('Spine-2', 'Leaf-2', 'fiber', 40000, 0.2, 99.99, 50),
                ('Spine-2', 'Leaf-3', 'fiber', 40000, 0.2, 99.99, 50),
                ('Spine-2', 'Leaf-4', 'fiber', 40000, 0.2, 99.99, 50),
                ('Spine-2', 'Leaf-5', 'fiber', 40000, 0.2, 99.99, 50),
                ('Spine-3', 'Leaf-1', 'fiber', 40000, 0.2, 99.99, 50),
                ('Spine-3', 'Leaf-3', 'fiber', 40000, 0.2, 99.99, 50),
                ('Spine-3', 'Leaf-5', 'fiber', 40000, 0.2, 99.99, 50),
                # Leaf to servers
                ('Leaf-1', 'Rack A1', 'ethernet', 10000, 0.5, 99.9, 10),
                ('Leaf-1', 'Rack A2', 'ethernet', 10000, 0.5, 99.9, 12),
                ('Leaf-2', 'Rack A1', 'ethernet', 10000, 0.5, 99.9, 10),
                ('Leaf-2', 'Rack B1', 'ethernet', 10000, 0.5, 99.9, 10),
                ('Leaf-3', 'Rack B1', 'ethernet', 10000, 0.5, 99.9, 10),
                ('Leaf-3', 'Rack B2', 'ethernet', 10000, 0.5, 99.9, 12),
                ('Leaf-4', 'Rack C1', 'ethernet', 10000, 0.5, 99.9, 10),
                ('Leaf-4', 'Rack C2', 'ethernet', 10000, 0.5, 99.9, 12),
                ('Leaf-5', 'Rack C2', 'ethernet', 10000, 0.5, 99.9, 10),
                ('Leaf-5', 'Storage Node', 'fiber', 40000, 0.3, 99.5, 15),
            ]
            for s, t, ct, bw, lat, rel, dist in c3:
                Connection.objects.create(
                    topology=topo3, source=n[s], target=n[t],
                    connection_type=ct, bandwidth=bw, latency=lat, reliability=rel,
                    distance=dist, is_active=True,
                )

        # ---- Smart City IoT Network ----
        topo4, _ = NetworkTopology.objects.get_or_create(name='Smart City IoT Network', defaults={
            'description': 'City-wide IoT sensor network with wireless links, long-range repeaters, and a central NOC'
        })
        if topo4.nodes.count() == 0:
            n = {}
            nd = [
                ('NOC Server', 'server', 350, 50, 'active', 1000, 2, '10.100.0.1'),
                ('City Gateway A', 'gateway', 150, 150, 'active', 500, 3, '10.100.1.1'),
                ('City Gateway B', 'gateway', 550, 150, 'active', 500, 3, '10.100.1.2'),
                ('District Hub N', 'hub', 200, 280, 'active', 200, 5, '10.100.2.1'),
                ('District Hub E', 'hub', 500, 280, 'active', 200, 5, '10.100.2.2'),
                ('District Hub S', 'hub', 350, 420, 'active', 200, 5, '10.100.2.3'),
                ('District Hub W', 'hub', 100, 370, 'active', 200, 5, '10.100.2.4'),
                ('Repeater Tower 1', 'repeater', 350, 220, 'active', 50, 8, None),
                ('Repeater Tower 2', 'repeater', 160, 500, 'active', 50, 8, None),
                ('Repeater Tower 3', 'repeater', 540, 500, 'active', 50, 8, None),
                ('Traffic Sensors N', 'endpoint', 200, 380, 'active', 10, 20, '10.100.3.1'),
                ('Traffic Sensors E', 'endpoint', 480, 380, 'active', 10, 20, '10.100.3.2'),
                ('Traffic Sensors S', 'endpoint', 350, 520, 'active', 10, 20, '10.100.3.3'),
                ('Air Quality Grid', 'endpoint', 230, 470, 'active', 5, 30, '10.100.4.1'),
                ('Power Grid Sensors', 'endpoint', 480, 470, 'active', 5, 30, '10.100.4.2'),
                ('AP Public Square', 'access_point', 350, 330, 'active', 300, 5, '10.100.5.1'),
                ('AP Train Station', 'access_point', 550, 420, 'active', 300, 5, '10.100.5.2'),
                ('AP City Hall', 'access_point', 150, 420, 'active', 300, 5, '10.100.5.3'),
                ('Firewall Edge', 'firewall', 350, 110, 'active', 500, 2, '10.100.0.254'),
                ('Isolated Sensor', 'endpoint', 650, 550, 'active', 5, 30, '10.100.9.1'),
            ]
            for name, ntype, x, y, status, cap, delay, ip in nd:
                n[name] = Node.objects.create(
                    topology=topo4, name=name, node_type=ntype,
                    x_pos=x, y_pos=y, status=status,
                    capacity=cap, processing_delay=delay, ip_address=ip,
                )
            c4 = [
                ('NOC Server', 'Firewall Edge', 'fiber', 1000, 1, 99.9, 80),
                ('Firewall Edge', 'City Gateway A', 'fiber', 500, 2, 99.5, 500),
                ('Firewall Edge', 'City Gateway B', 'fiber', 500, 2, 99.5, 500),
                ('City Gateway A', 'District Hub N', 'wifi', 200, 8, 96, 1200),
                ('City Gateway A', 'District Hub W', 'wifi', 200, 10, 94, 1800),
                ('City Gateway B', 'District Hub E', 'wifi', 200, 8, 96, 1200),
                ('City Gateway B', 'Repeater Tower 3', 'microwave', 50, 15, 91, 2500),
                ('District Hub N', 'Repeater Tower 1', 'wifi', 50, 12, 92, 900),
                ('District Hub N', 'Traffic Sensors N', 'wifi', 10, 25, 88, 600),
                ('District Hub N', 'AP City Hall', 'wifi', 200, 6, 95, 400),
                ('District Hub E', 'Traffic Sensors E', 'wifi', 10, 25, 88, 700),
                ('District Hub E', 'AP Train Station', 'wifi', 200, 6, 95, 350),
                ('District Hub E', 'Power Grid Sensors', 'wifi', 5, 35, 85, 900),
                ('District Hub S', 'Traffic Sensors S', 'wifi', 10, 25, 88, 500),
                ('District Hub S', 'Air Quality Grid', 'wifi', 5, 30, 86, 700),
                ('District Hub W', 'AP City Hall', 'wifi', 200, 6, 95, 300),
                ('District Hub W', 'Air Quality Grid', 'wifi', 5, 35, 85, 800),
                ('Repeater Tower 1', 'District Hub S', 'microwave', 50, 18, 90, 3000),
                ('Repeater Tower 1', 'AP Public Square', 'wifi', 200, 8, 93, 400),
                ('Repeater Tower 2', 'District Hub S', 'wifi', 50, 20, 89, 1500),
                ('Repeater Tower 2', 'District Hub W', 'wifi', 50, 15, 91, 1200),
                ('Repeater Tower 3', 'District Hub S', 'wifi', 50, 18, 90, 1800),
                ('AP Public Square', 'AP City Hall', 'wifi', 200, 5, 95, 350),
            ]
            for s, t, ct, bw, lat, rel, dist in c4:
                Connection.objects.create(
                    topology=topo4, source=n[s], target=n[t],
                    connection_type=ct, bandwidth=bw, latency=lat, reliability=rel,
                    distance=dist, is_active=True,
                )

        # ---- Enterprise WAN ----
        topo5, _ = NetworkTopology.objects.get_or_create(name='Enterprise Multi-Site WAN', defaults={
            'description': 'Multinational enterprise WAN connecting 5 office sites via fiber, MPLS, and satellite backup'
        })
        if topo5.nodes.count() == 0:
            n = {}
            nd = [
                # HQ
                ('HQ Core Router', 'router', 350, 200, 'active', 10000, 1, '10.0.0.1'),
                ('HQ Firewall', 'firewall', 350, 120, 'active', 5000, 2, '10.0.0.254'),
                ('HQ LB', 'load_balancer', 350, 280, 'active', 5000, 1, '10.0.0.10'),
                ('HQ Switch A', 'switch', 240, 360, 'active', 1000, 1, '10.0.1.1'),
                ('HQ Switch B', 'switch', 460, 360, 'active', 1000, 1, '10.0.1.2'),
                ('HQ App Server', 'server', 200, 450, 'active', 1000, 2, '10.0.2.1'),
                ('HQ DB Cluster', 'server', 310, 450, 'active', 1000, 2, '10.0.2.2'),
                ('HQ DR Server', 'server', 420, 450, 'active', 1000, 2, '10.0.2.3'),
                # Branch offices
                ('Branch NY Router', 'router', 100, 120, 'active', 1000, 2, '10.1.0.1'),
                ('Branch NY Switch', 'switch', 100, 220, 'active', 1000, 1, '10.1.1.1'),
                ('Branch NY AP', 'access_point', 100, 310, 'active', 300, 3, '10.1.2.1'),
                ('Branch LA Router', 'router', 600, 120, 'active', 1000, 2, '10.2.0.1'),
                ('Branch LA Switch', 'switch', 600, 220, 'active', 1000, 1, '10.2.1.1'),
                ('Branch LA AP', 'access_point', 600, 310, 'active', 300, 3, '10.2.2.1'),
                ('Branch LON Router', 'router', 150, 480, 'active', 1000, 2, '10.3.0.1'),
                ('Branch LON Switch', 'switch', 150, 560, 'active', 1000, 1, '10.3.1.1'),
                ('Branch SYD Router', 'router', 550, 480, 'active', 500, 5, '10.4.0.1'),
                ('Branch SYD Switch', 'switch', 550, 560, 'active', 500, 1, '10.4.1.1'),
                # WAN edge / satellite backup
                ('WAN Edge Router', 'router', 350, 50, 'active', 5000, 1, '10.0.0.100'),
                ('Satellite Uplink', 'repeater', 500, 50, 'active', 100, 600, None),
            ]
            for name, ntype, x, y, status, cap, delay, ip in nd:
                n[name] = Node.objects.create(
                    topology=topo5, name=name, node_type=ntype,
                    x_pos=x, y_pos=y, status=status,
                    capacity=cap, processing_delay=delay, ip_address=ip,
                )
            c5 = [
                # HQ internal
                ('HQ Firewall', 'WAN Edge Router', 'fiber', 5000, 1, 99.9, 10),
                ('HQ Firewall', 'HQ Core Router', 'fiber', 5000, 1, 99.99, 5),
                ('HQ Core Router', 'HQ LB', 'fiber', 5000, 0.5, 99.99, 5),
                ('HQ LB', 'HQ Switch A', 'fiber', 1000, 1, 99.9, 10),
                ('HQ LB', 'HQ Switch B', 'fiber', 1000, 1, 99.9, 10),
                ('HQ Switch A', 'HQ App Server', 'ethernet', 1000, 1, 99.9, 20),
                ('HQ Switch A', 'HQ DB Cluster', 'ethernet', 1000, 1, 99.9, 20),
                ('HQ Switch B', 'HQ DB Cluster', 'ethernet', 1000, 1, 99.9, 20),
                ('HQ Switch B', 'HQ DR Server', 'ethernet', 1000, 1, 99.9, 20),
                # WAN links (MPLS fiber)
                ('WAN Edge Router', 'Branch NY Router', 'fiber', 1000, 12, 99.5, 350000),
                ('WAN Edge Router', 'Branch LA Router', 'fiber', 1000, 18, 99.5, 450000),
                ('WAN Edge Router', 'Branch LON Router', 'fiber', 1000, 85, 99.2, 900000),
                ('WAN Edge Router', 'Branch SYD Router', 'fiber', 500, 180, 98.5, 1600000),
                # Satellite backup for Sydney
                ('WAN Edge Router', 'Satellite Uplink', 'microwave', 100, 10, 99, 50),
                ('Satellite Uplink', 'Branch SYD Router', 'satellite', 100, 600, 95, 36000000),
                # Cross-branch links
                ('Branch NY Router', 'Branch LA Router', 'fiber', 500, 25, 99, 600000),
                ('Branch LON Router', 'Branch SYD Router', 'fiber', 200, 280, 97, 1700000),
                # Branch internals
                ('Branch NY Router', 'Branch NY Switch', 'ethernet', 1000, 1, 99.9, 20),
                ('Branch NY Switch', 'Branch NY AP', 'ethernet', 300, 2, 99, 30),
                ('Branch LA Router', 'Branch LA Switch', 'ethernet', 1000, 1, 99.9, 20),
                ('Branch LA Switch', 'Branch LA AP', 'ethernet', 300, 2, 99, 30),
                ('Branch LON Router', 'Branch LON Switch', 'ethernet', 1000, 1, 99.9, 20),
                ('Branch SYD Router', 'Branch SYD Switch', 'ethernet', 500, 1, 99.9, 20),
            ]
            for s, t, ct, bw, lat, rel, dist in c5:
                Connection.objects.create(
                    topology=topo5, source=n[s], target=n[t],
                    connection_type=ct, bandwidth=bw, latency=lat, reliability=rel,
                    distance=dist, is_active=True,
                )

        # ---- Hospital Emergency Network ----
        topo6, _ = NetworkTopology.objects.get_or_create(name='Hospital Critical Network', defaults={
            'description': 'Hospital emergency communication network — life-critical systems with strict redundancy requirements'
        })
        if topo6.nodes.count() == 0:
            n = {}
            nd = [
                ('Core Switch A', 'switch', 280, 160, 'active', 10000, 0.5, '192.168.0.1'),
                ('Core Switch B', 'switch', 420, 160, 'active', 10000, 0.5, '192.168.0.2'),
                ('Hospital Firewall', 'firewall', 350, 60, 'active', 5000, 1, '192.168.0.254'),
                ('Internet Gateway', 'gateway', 350, 0, 'active', 1000, 2, '203.0.113.1'),
                ('EMR Server', 'server', 180, 280, 'active', 2000, 2, '192.168.1.1'),
                ('PACS Imaging', 'server', 350, 280, 'active', 5000, 3, '192.168.1.2'),
                ('Backup EMR', 'server', 520, 280, 'active', 2000, 2, '192.168.1.3'),
                ('ICU Switch', 'switch', 150, 400, 'active', 1000, 1, '192.168.2.1'),
                ('OR Switch', 'switch', 280, 420, 'active', 1000, 1, '192.168.2.2'),
                ('ER Switch', 'switch', 420, 420, 'active', 1000, 1, '192.168.2.3'),
                ('Ward Switch A', 'switch', 550, 400, 'active', 1000, 1, '192.168.2.4'),
                ('ICU Monitors', 'endpoint', 80, 520, 'active', 100, 5, '192.168.3.1'),
                ('ICU AP', 'access_point', 160, 520, 'active', 300, 3, '192.168.3.2'),
                ('OR Equipment', 'endpoint', 250, 540, 'active', 100, 5, '192.168.4.1'),
                ('OR AP', 'access_point', 330, 540, 'active', 300, 3, '192.168.4.2'),
                ('ER Terminals', 'endpoint', 400, 540, 'active', 100, 5, '192.168.5.1'),
                ('ER AP', 'access_point', 480, 540, 'active', 300, 3, '192.168.5.2'),
                ('Ward Terminals', 'endpoint', 560, 520, 'active', 50, 10, '192.168.6.1'),
                ('Nurse Call System', 'endpoint', 640, 400, 'active', 10, 20, '192.168.7.1'),
                ('Pharmacy Terminal', 'endpoint', 640, 280, 'degraded', 50, 15, '192.168.8.1'),
            ]
            for name, ntype, x, y, status, cap, delay, ip in nd:
                n[name] = Node.objects.create(
                    topology=topo6, name=name, node_type=ntype,
                    x_pos=x, y_pos=y, status=status,
                    capacity=cap, processing_delay=delay, ip_address=ip,
                )
            c6 = [
                ('Internet Gateway', 'Hospital Firewall', 'fiber', 1000, 2, 99.9, 30),
                ('Hospital Firewall', 'Core Switch A', 'fiber', 5000, 0.5, 99.99, 20),
                ('Hospital Firewall', 'Core Switch B', 'fiber', 5000, 0.5, 99.99, 20),
                ('Core Switch A', 'Core Switch B', 'fiber', 10000, 0.2, 99.99, 15),
                ('Core Switch A', 'EMR Server', 'fiber', 2000, 1, 99.99, 30),
                ('Core Switch A', 'PACS Imaging', 'fiber', 5000, 1, 99.99, 25),
                ('Core Switch B', 'PACS Imaging', 'fiber', 5000, 1, 99.99, 25),
                ('Core Switch B', 'Backup EMR', 'fiber', 2000, 1, 99.99, 30),
                ('Core Switch A', 'ICU Switch', 'fiber', 1000, 1, 99.99, 60),
                ('Core Switch A', 'OR Switch', 'fiber', 1000, 1, 99.99, 80),
                ('Core Switch B', 'ER Switch', 'fiber', 1000, 1, 99.99, 70),
                ('Core Switch B', 'Ward Switch A', 'fiber', 1000, 1, 99.99, 90),
                # Ward switch A is the only path to Nurse Call and Pharmacy — creates failure points
                ('Ward Switch A', 'Nurse Call System', 'ethernet', 10, 5, 97, 80),
                ('Ward Switch A', 'Pharmacy Terminal', 'ethernet', 50, 8, 93, 120),
                ('Ward Switch A', 'Ward Terminals', 'ethernet', 100, 2, 99, 50),
                ('ICU Switch', 'ICU Monitors', 'ethernet', 100, 2, 99.5, 40),
                ('ICU Switch', 'ICU AP', 'wifi', 300, 3, 98, 30),
                ('OR Switch', 'OR Equipment', 'ethernet', 100, 2, 99.9, 35),
                ('OR Switch', 'OR AP', 'wifi', 300, 3, 98, 25),
                ('ER Switch', 'ER Terminals', 'ethernet', 100, 2, 99.5, 45),
                ('ER Switch', 'ER AP', 'wifi', 300, 3, 97, 35),
            ]
            for s, t, ct, bw, lat, rel, dist in c6:
                Connection.objects.create(
                    topology=topo6, source=n[s], target=n[t],
                    connection_type=ct, bandwidth=bw, latency=lat, reliability=rel,
                    distance=dist, is_active=True,
                )

        # ---- Extra rulesets ----
        rs2, _ = RuleSet.objects.get_or_create(name='IoT / Wireless Standards', defaults={
            'description': 'Relaxed rules suited for wireless and IoT networks with higher latency tolerance',
            'is_default': False,
        })
        iot_rules = [
            ('Max Wireless Latency', 'max_latency', 200, 'warning', 'IoT links may have up to 200ms'),
            ('Min IoT Bandwidth', 'min_bandwidth', 1, 'warning', 'IoT sensors only need 1 Mbps'),
            ('Min Wireless Reliability', 'min_reliability', 85, 'critical', 'Wireless links must be at least 85%'),
            ('Max Wireless Distance', 'max_distance', 5000, 'warning', 'Flag wireless links over 5km'),
            ('Min Node Connections', 'min_connections', 1, 'critical', 'All IoT nodes need at least 1 uplink'),
            ('Max Hop Count IoT', 'max_hop_count', 8, 'warning', 'IoT paths up to 8 hops acceptable'),
        ]
        for name, rtype, threshold, severity, desc in iot_rules:
            Rule.objects.get_or_create(ruleset=rs2, name=name, defaults={
                'rule_type': rtype, 'threshold': threshold, 'severity': severity,
                'description': desc, 'is_enabled': True,
            })

        rs3, _ = RuleSet.objects.get_or_create(name='Critical Infrastructure', defaults={
            'description': 'Strict rules for life-critical and industrial systems with zero tolerance for single points of failure',
            'is_default': False,
        })
        crit_rules = [
            ('Max Latency Strict', 'max_latency', 10, 'critical', 'Critical systems must have <10ms latency'),
            ('Min Bandwidth Critical', 'min_bandwidth', 100, 'critical', 'All critical links need >= 100 Mbps'),
            ('Min Reliability Critical', 'min_reliability', 99.9, 'critical', 'Critical links must be 99.9%+ reliable'),
            ('Max Distance Critical', 'max_distance', 500, 'warning', 'Physical distance should stay under 500m'),
            ('Min Redundancy Critical', 'min_redundancy', 3, 'critical', 'All critical node pairs need 3 paths'),
            ('Max Connections', 'max_connections', 10, 'warning', 'Flag overloaded nodes'),
            ('Min Connections Critical', 'min_connections', 2, 'critical', 'All critical nodes need >= 2 connections'),
            ('Max Hop Count Strict', 'max_hop_count', 4, 'critical', 'Critical paths must not exceed 4 hops'),
        ]
        for name, rtype, threshold, severity, desc in crit_rules:
            Rule.objects.get_or_create(ruleset=rs3, name=name, defaults={
                'rule_type': rtype, 'threshold': threshold, 'severity': severity,
                'description': desc, 'is_enabled': True,
            })

        self.stdout.write(self.style.SUCCESS('Demo data seeded successfully!'))
        self.stdout.write('  - 6 network topologies')
        self.stdout.write('  - 3 rulesets with 22 rules total')
        self.stdout.write('  - Run: python manage.py runserver')
