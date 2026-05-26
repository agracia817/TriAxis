import os
import textwrap
import traceback
from triaxis.apps.apps import CodeApp, OfficeApp, GravityApp, DriveApp
from triaxis.template_engine import TemplateEngine


# ---------------------------------------------------------
#  VIRTUAL FILE SYSTEM (AMB MILLOR GESTIÓ DE PATHS)
# ---------------------------------------------------------
class VirtualFileSystem:
    def __init__(self):
        self.files = {}  # { "/path/file.txt": "content" }

    def _norm(self, path):
        if not path.startswith("/"):
            path = "/" + path
        return os.path.normpath(path).replace("\\", "/")

    def write(self, path, content):
        self.files[self._norm(path)] = content

    def read(self, path):
        return self.files.get(self._norm(path), "")

    def append(self, path, content):
        p = self._norm(path)
        self.files[p] = self.files.get(p, "") + content

    def listdir(self, prefix="/"):
        prefix = self._norm(prefix)
        plen = len(prefix.rstrip("/")) + 1

        children = set()
        for p in self.files:
            if p.startswith(prefix):
                rest = p[plen:]
                if rest and "/" not in rest:
                    children.add(rest)

        return sorted(children)


# ---------------------------------------------------------
#  SCRIPT EXECUTOR (SANDBOX SEGURA)
# ---------------------------------------------------------
class ScriptExecutor:
    SAFE_BUILTINS = {
        "len": len,
        "range": range,
        "str": str,
        "int": int,
        "float": float,
        "bool": bool,
        "print": print,
    }

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
            exec(
                textwrap.dedent(code),
                {"__builtins__": ScriptExecutor.SAFE_BUILTINS},
                env
            )
        except Exception as e:
            tb = traceback.format_exc(limit=2)
            out_buf.append(f"[ERROR] {e}\n{tb}")

        if out_buf:
            self.vfs.append(log_path, "\n".join(out_buf) + "\n")

        return "\n".join(out_buf)


# ---------------------------------------------------------
#  OS KERNEL (NET, MODULAR, AMB TOTES LES APPS)
# ---------------------------------------------------------
class OSKernel:
    def __init__(self, graph_state=None):
        self.vfs = VirtualFileSystem()
        self.graph = graph_state
        self.executor = ScriptExecutor(self.vfs, self.graph)
        self.templates = TemplateEngine()

        self.apps = {
            "code": CodeApp(self),
            "office": OfficeApp(self),
            "gravity": GravityApp(self),
            "drive": DriveApp(self),
        }

    def get_app(self, name: str):
        return self.apps.get(name)

    # ---------------- OS API ----------------

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
