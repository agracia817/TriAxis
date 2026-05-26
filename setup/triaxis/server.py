from flask import Flask, request, Response
from triaxis.twos import OSKernel
from triaxis.graph import GraphState
from triaxis.runtime import RuntimeContext, parse_tsl
import html

app = Flask(__name__)

kernel = OSKernel(GraphState())
ctx = RuntimeContext()

@app.route("/")
def index():
    return (
        "<h1>TriAxis Web OS</h1>"
        "<p>Envia TSL a /run (POST) o obre apps a /app/&lt;nom&gt;/&lt;path&gt;</p>"
    )

@app.route("/run", methods=["POST"])
def run_tsl():
    tsl = request.get_data(as_text=True)
    # Preserve empty lines so OS:WRITE buffers work correctly
    lines = tsl.splitlines()
    outputs = []

    for line in lines:
        # process blank lines when inside a buffer
        if not line.strip() and not ctx.current_app:
            continue

        try:
            result = parse_tsl(line, ctx, kernel, kernel.graph)
        except Exception as e:
            # capture exception and continue, log to kernel logs
            err = f"[PARSER ERROR] {type(e).__name__}: {e}"
            # append to logs (no overwrite)
            kernel.os_write("/logs/parser_errors.txt", kernel.os_read("/logs/parser_errors.txt") + err + "\n")
            outputs.append(html.escape(err))
            continue

        # render result safely for HTML
        outputs.append(html.escape(str(result)))

    body = "<br>".join(outputs) or "(no output)"
    return Response(body, content_type="text/html; charset=utf-8")

@app.route("/drive", defaults={"path": ""})
@app.route("/drive/<path:path>")
def drive_list(path):
    app_obj = kernel.get_app("drive")
    return app_obj.list_dir("/" + path if path else "/")

@app.route("/drive/create", methods=["POST"])
def drive_create():
    path = request.form.get("path", "/")
    name = request.form["name"]
    app_obj = kernel.get_app("drive")
    return app_obj.create_file(path, name)

@app.route("/app/<name>/<path:path>")
def open_app(name, path):
    app_obj = kernel.get_app(name)
    if not app_obj:
        return f"No such app: {name}", 404

    full_path = "/" + path

    if name == "code":
        return app_obj.open_file(full_path)

    if name == "office":
        return app_obj.open_doc(full_path)

    if name == "gravity":
        return app_obj.set_goal(path)

    return "App not implemented", 501

if __name__ == "__main__":
    # Executa com a mòdul preferiblement: python -m triaxis.server
    app.run(host="0.0.0.0", port=8080)
