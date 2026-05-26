class NMLNode:
    def __init__(self, node_id):
        self.id = node_id
        self.text = ""
        self.type = ""
        self.semantics = ""
        self.intent = ""
        self.links = []

def load_nml_file(path):
    nodes = {}
    current = None

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            if line.startswith("#NODE"):
                node_id = line.split()[1]
                current = NMLNode(node_id)
                nodes[node_id] = current
                continue

            if line.startswith("text:"):
                current.text = line[5:].strip()
            elif line.startswith("type:"):
                current.type = line[5:].strip()
            elif line.startswith("semantics:"):
                current.semantics = line[10:].strip()
            elif line.startswith("intent:"):
                current.intent = line[7:].strip()
            elif line.startswith("-"):
                rel, target = line[1:].split("->")
                current.links.append((rel.strip(), target.strip()))

    return nodes
