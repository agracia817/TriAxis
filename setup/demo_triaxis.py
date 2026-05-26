from triaxis.twos import OSKernel
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

print("\nHTML editor:\n", html_editor)
print("\nHTML output:\n", html_output)
