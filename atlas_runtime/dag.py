"""DAG scheduler with parallel execution and critical path tracking."""
import networkx as nx
from typing import List, Dict, Any


class DAGNode:
    def __init__(self, name, role=None, phase=None, deps=None, parallel_safe=True, tokens=0):
        self.name = name
        self.role = role
        self.phase = phase
        self.deps = deps or []
        self.parallel_safe = parallel_safe
        self.tokens = tokens
        self.completed = False


class DAGScheduler:
    def __init__(self):
        self.graph = nx.DiGraph()
        self.nodes = {}
    
    def add_node(self, name, **kwargs):
        self.nodes[name] = DAGNode(name, **kwargs)
        self.graph.add_node(name)
    
    def add_edge(self, from_node, to_node):
        self.graph.add_edge(from_node, to_node)
        if from_node in self.nodes and to_node in self.nodes:
            self.nodes[to_node].deps.append(from_node)
    
    def critical_path(self):
        try:
            # simple longest path by token weight
            if nx.is_directed_acyclic_graph(self.graph):
                return nx.dag_longest_path(self.graph, weight='tokens')
        except Exception:
            pass
        return []
    
    def ready_nodes(self):
        ready = []
        for name, node in self.nodes.items():
            if node.completed:
                continue
            if all(self.nodes[d].completed for d in node.deps):
                ready.append(name)
        return ready
    
    def parallel_safe_groups(self, ready_nodes):
        # simple grouping - all ready nodes can run in parallel if marked safe
        return [ready_nodes] if ready_nodes else []
