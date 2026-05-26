import re

class RuntimeContext:
    def __init__(self):
        self.active_node_id = None
        self.current_app = None
        self.buffer = ""

def extract(tag, text):
    match = re.search(f'{tag}="([^"]+)"', text)
    return match.group(1) if match else None

def parse_tsl(token, ctx, kernel, graph, apps=None):
    token = token.strip()

    # OS:WRITE
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

    # OS:READ
    if token.startswith("<OS:READ"):
        path = extract("path", token)
        return ("OS_READ", path, kernel.os_read(path))

    # OS:LIST
    if token.startswith("<OS:LIST"):
        path = extract("path", token)
        return ("OS_LIST", path, kernel.os_list(path))

    # OS:EXEC
    if token.startswith("<OS:EXEC"):
        path = extract("path", token)
        out = kernel.os_exec(path)
        return ("OS_EXEC", path, out)

    # Buffer mode
    if ctx.current_app:
        ctx.buffer += token + "\n"
        return ("BUFFER_APPEND", token)

    # Default
    return ("TEXT", token)
