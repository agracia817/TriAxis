class BaseApp:
    def __init__(self, kernel):
        self.kernel = kernel

    def render(self):
        return "<div>App base</div>"

class CodeApp(BaseApp):
    def open_file(self, path: str):
        content = self.kernel.os_read(path)
        return self.kernel.templates.render(
            "base.html",
            CONTENT=self.kernel.templates.render(
                "code.html",
                PATH=path,
                CONTENT=content
            )
        )

    def run_file(self, path: str):
        out = self.kernel.os_exec(path)
        return self.kernel.templates.render(
            "base.html",
            CONTENT=self.kernel.templates.render(
                "code_output.html",
                PATH=path,
                OUTPUT=out
            )
        )

class OfficeApp(BaseApp):
    def open_doc(self, path: str):
        content = self.kernel.os_read(path)
        return self.kernel.templates.render(
            "base.html",
            CONTENT=self.kernel.templates.render(
                "office.html",
                PATH=path,
                CONTENT=content
            )
        )

class DriveApp(BaseApp):
    def list_dir(self, path="/"):
        files = self.kernel.os_list(path)
        items = []

        for f in files:
            # Decideix quin app obrir segons extensió
            if f.endswith(".py"):
                url = f"/app/code{f}"
            elif f.endswith(".txt") or f.endswith(".md"):
                url = f"/app/office{f}"
            else:
                url = f"/drive{f}"

            items.append(f'<li><a href="{url}">{f}</a></li>')

        html_list = "\n".join(items)

        return self.kernel.templates.render(
            "base.html",
            CONTENT=self.kernel.templates.render(
                "drive.html",
                PATH=path,
                FILES=html_list
            )
        )

    def create_file(self, path, name):
        full = f"{path}/{name}".replace("//", "/")
        self.kernel.os_write(full, "")
        return self.list_dir(path)


class GravityApp(BaseApp):
    def set_goal(self, goal: str):
        return self.kernel.templates.render(
            "base.html",
            CONTENT=self.kernel.templates.render(
                "gravity.html",
                GOAL=goal,
                PROJECT=""
            )
        )

    def render_project(self, name: str):
        return self.kernel.templates.render(
            "base.html",
            CONTENT=self.kernel.templates.render(
                "gravity.html",
                GOAL="",
                PROJECT=name
            )
        )

