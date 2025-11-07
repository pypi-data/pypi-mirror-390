import os

class Router:
    def __init__(self, path):
        self.path = path
        self.routes = {}

    def add_route(self, path, filename):
        self.routes[path] = filename
        print(f"🔗 مسیر {path} → {filename} ثبت شد")

    def generate_links(self):
        links = ""
        for route, file in self.routes.items():
            links += f'<a href="{file}">{route}</a> | '
        return links