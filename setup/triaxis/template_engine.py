import os

class TemplateEngine:
    def __init__(self, base_path="triaxis/apps/web"):
        self.base_path = base_path

    def load(self, name: str):
        path = os.path.join(self.base_path, name)
        with open(path, "r", encoding="utf-8") as f:
            return f.read()

    def render(self, template_name: str, **kwargs):
        html = self.load(template_name)
        for key, value in kwargs.items():
            html = html.replace(f"{{{{{key}}}}}", value)
        return html
