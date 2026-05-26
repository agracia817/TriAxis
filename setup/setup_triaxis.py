import os

print("🚀 Desplegant TriAxis-Graph + TWOS + TSL + Apps v3...")

# ---------------------------------------------------------
# DIRECTORIS
# ---------------------------------------------------------

DIRS = [
    "triaxis",
    "triaxis/apps",
    "triaxis/apps/web",
    "triaxis/kernel",
    "triaxis/vfs",
    "data",
]

# ---------------------------------------------------------
# FITXERS
# ---------------------------------------------------------

FILES = {}

# __init__
FILES["triaxis/__init__.py"] = ""

# graph.py
FILES["triaxis/graph.py"] = """import torch

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
"""

# twos.py
FILES["triaxis/twos.py"] = """import textwrap
from .apps.apps import CodeApp, OfficeApp, GravityApp

class VirtualFileSystem:
    def __init__(self):
        self.files = {}

    def write(self, path, content):
        self.files[path] = content

    def read(self, path):
        return self.files.get(path, "")

    def append(self, path, content):
        self.files[path] = self.files.get(path, "") + content

    def listdir(self, prefix="/"):
        return [p for p in self.files if p.startswith(prefix)]

class ScriptExecutor:
    def __init__(self, vfs, graph=None):
        self.vfs = vfs
        self.graph = graph

    def run(self, code, log_path="/logs/output.txt"):
        out_buf = []

        def _print(*args):
            msg = " ".join(str(a) for a in args)
            out_buf.append(msg)

        env = {
            "print": _print,
            "vfs": self.vfs,
            "graph": self.graph,
        }

        try:
            exec(textwrap.dedent(code), {"__builtins__": {}}, env)
        except Exception as e:
            out_buf.append(f"[ERROR] {e}")

        if out_buf:
            self.vfs.append(log_path, "\\n".join(out_buf) + "\\n")

        return "\\n".join(out_buf)

class OSKernel:
    def __init__(self, graph_state=None):
        self.vfs = VirtualFileSystem()
        self.graph = graph_state
        self.executor = ScriptExecutor(self.vfs, self.graph)
        self.apps = {
            "code": CodeApp(self),
            "office": OfficeApp(self),
            "gravity": GravityApp(self),
        }

    def os_write(self, path, content):
        self.vfs.write(path, content)

    def os_read(self, path):
        return self.vfs.read(path)

    def os_list(self, prefix="/"):
        return self.vfs.listdir(prefix)

    def os_exec(self, path, log_path="/logs/output.txt"):
        code = self.vfs.read(path)
        if not code:
            return f"[OS] No script at {path}"
        return self.executor.run(code, log_path)

    def get_app(self, name: str):
        return self.apps.get(name)
"""

# runtime.py
FILES["triaxis/runtime.py"] = """import re

class RuntimeContext:
    def __init__(self):
        self.active_node_id = None
        self.current_app = None
        self.buffer = ""

def extract(tag, text):
    try:
        return re.search(f'{tag}="([^"]+)"', text).group(1)
    except:
        return None

def parse_tsl(token, ctx, kernel, graph, apps=None):
    token = token.strip()

    if token.startswith("<OS:WRITE"):
        path = extract("path", token)
        ctx.buffer = ""
        ctx.current_app = ("OS_WRITE", path)
        return ("OS_WRITE_BEGIN", path)

    if token == "</OS:WRITE>":
        mode, path = ctx.current_app
        kernel.os_write(path, ctx.buffer)
        ctx.buffer = ""
        ctx.current_app = None
        return ("OS_WRITE_END", path)

    if token.startswith("<OS:READ"):
        path = extract("path", token)
        return ("OS_READ", path, kernel.os_read(path))

    if token.startswith("<OS:LIST"):
        path = extract("path", token)
        return ("OS_LIST", path, kernel.os_list(path))

    if token.startswith("<OS:EXEC"):
        path = extract("path", token)
        out = kernel.os_exec(path)
        return ("OS_EXEC", path, out)

    if ctx.current_app:
        ctx.buffer += token + "\\n"
        return ("BUFFER_APPEND", token)

    return ("TEXT", token)
"""

# data.py
FILES["triaxis/data.py"] = """class NMLNode:
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
"""

# apps/__init__.py
FILES["triaxis/apps/__init__.py"] = ""

# apps/apps.py
FILES["triaxis/apps/apps.py"] = """class BaseApp:
    def __init__(self, kernel):
        self.kernel = kernel

    def render(self):
        return "<div>App base</div>"

class CodeApp(BaseApp):
    def open_file(self, path: str):
        content = self.kernel.os_read(path)
        return self.render_editor(path, content)

    def render_editor(self, path: str, content: str):
        return f\"\"\"<div class="code-app">
  <h2>Code: {path}</h2>
  <pre><code>{content}</code></pre>
  <button>Run</button>
</div>\"\"\"

    def run_file(self, path: str):
        out = self.kernel.os_exec(path)
        return f\"\"\"<div class="code-output">
  <h3>Output: {path}</h3>
  <pre>{out}</pre>
</div>\"\"\"

class OfficeApp(BaseApp):
    def open_doc(self, path: str):
        content = self.kernel.os_read(path)
        return f\"\"\"<div class="office-app">
  <h2>Document: {path}</h2>
  <textarea rows="20" cols="80">{content}</textarea>
</div>\"\"\"

class GravityApp(BaseApp):
    def set_goal(self, goal: str):
        return f\"\"\"<div class="gravity-app">
  <h2>Goal</h2>
  <p>{goal}</p>
</div>\"\"\"

    def render_project(self, name: str):
        return f\"\"\"<div class="gravity-project">
  <h2>Project: {name}</h2>
  <p>(Aquí TriAxis generaria estructura de projecte, fitxers, etc.)</p>
</div>\"\"\"
"""

# kernel/__init__.py
FILES["triaxis/kernel/__init__.py"] = ""

# web templates
FILES["triaxis/apps/web/base.html"] = """<!DOCTYPE html>
<html lang="ca">
<head>
  <meta charset="UTF-8">
  <title>TriAxis Web OS</title>
  <style>
    body { font-family: sans-serif; margin: 0; display: flex; height: 100vh; }
    .sidebar { width: 220px; background: #111827; color: #e5e7eb; padding: 1rem; }
    .sidebar h1 { font-size: 1.1rem; margin-bottom: 1rem; }
    .sidebar a { display: block; color: #9ca3af; text-decoration: none; margin: 0.3rem 0; }
    .sidebar a:hover { color: #e5e7eb; }
    .main { flex: 1; padding: 1rem; background: #f3f4f6; overflow: auto; }
    .card { background: white; border-radius: 0.5rem; padding: 1rem; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
    pre { background: #111827; color: #e5e7eb; padding: 0.5rem; border-radius: 0.25rem; overflow-x: auto; }
    textarea { width: 100%; box-sizing: border-box; }
    button { padding: 0.4rem 0.8rem; margin-top: 0.5rem; }
  </style>
</head>
<body>
  <div class="sidebar">
    <h1>TriAxis OS</h1>
    <a href="#drive">Drive</a>
    <a href="#code">Code</a>
    <a href="#office">Office</a>
    <a href="#gravity">Gravity</a>
  </div>
  <div class="main">
    {{CONTENT}}
  </div>
</body>
</html>
"""

FILES["triaxis/apps/web/code.html"] = """<div class="card">
  <h2>Code: {{PATH}}</h2>
  <pre><code>{{CONTENT}}</code></pre>
  <button>Run</button>
</div>
"""

FILES["triaxis/apps/web/office.html"] = """<div class="card">
  <h2>Document: {{PATH}}</h2>
  <textarea rows="20" cols="80">{{CONTENT}}</textarea>
</div>
"""

FILES["triaxis/apps/web/gravity.html"] = """<div class="card">
  <h2>Gravity</h2>
  <p>Goal: {{GOAL}}</p>
  <p>Project: {{PROJECT}}</p>
</div>
"""

# demo_triaxis.py
FILES["demo_triaxis.py"] = """from triaxis.twos import OSKernel
from triaxis.graph import GraphState
from triaxis.runtime import RuntimeContext, parse_tsl

graph = GraphState()
kernel = OSKernel(graph)
ctx = RuntimeContext()

commands = [
    '<OS:WRITE path="/apps/code/test.py">',
    'print("Hola TWOS!")',
    '</OS:WRITE>',
    '<OS:EXEC path="/apps/code/test.py">'
]

for cmd in commands:
    result = parse_tsl(cmd, ctx, kernel, graph)
    print("TSL:", cmd, "=>", result)

code_app = kernel.get_app("code")
kernel.os_write("/drive/projects/demo.py", 'print("Hola des del CodeApp")')
html_editor = code_app.open_file("/drive/projects/demo.py")
html_output = code_app.run_file("/drive/projects/demo.py")

print("\\nHTML editor:\\n", html_editor)
print("\\nHTML output:\\n", html_output)
"""

# corpus
FILES["data/corpus.nml"] = "#NODE example\ntext: Exemple de corpus inicial\n"

# ---------------------------------------------------------
# CREACIÓ SEGURA
# ---------------------------------------------------------

for d in DIRS:
    os.makedirs(d, exist_ok=True)

for path, content in FILES.items():
    dirpath = os.path.dirname(path)

    # PATCH: evita errors si dirpath és buit
    if dirpath and not os.path.exists(dirpath):
        os.makedirs(dirpath, exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

print("✔ TriAxis v3 desplegat correctament.")
print("Ara pots executar: python demo_triaxis.py")
