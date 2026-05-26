import torch

class GraphState:
    def __init__(self, node_dim=128, edge_dim=128, device="cpu"):
        self.node_dim = node_dim
        self.edge_dim = edge_dim
        self.device = device
        self.nodes = {}
        self.edges = []

    def add_node(self, node_id, vec):
        self.nodes[node_id] = vec

    def add_edge(self, src, dst, rel, vec):
        self.edges.append((src, dst, rel, vec))

    def as_tensors(self):
        if not self.nodes:
            return None, None, None, None

        node_ids = list(self.nodes.keys())
        node_vecs = torch.stack([
            v if v is not None else torch.zeros(self.node_dim)
            for v in self.nodes.values()
        ])

        if not self.edges:
            edge_index = torch.empty(2, 0, dtype=torch.long)
            edge_vecs = torch.empty(0, self.edge_dim)
        else:
            src, dst, evecs = [], [], []
            id_to_idx = {nid: i for i, nid in enumerate(node_ids)}
            for s, d, rel, ev in self.edges:
                src.append(id_to_idx[s])
                dst.append(id_to_idx[d])
                evecs.append(ev if ev is not None else torch.zeros(self.edge_dim))
            edge_index = torch.tensor([src, dst], dtype=torch.long)
            edge_vecs = torch.stack(evecs)

        return node_ids, node_vecs, edge_index, edge_vecs
