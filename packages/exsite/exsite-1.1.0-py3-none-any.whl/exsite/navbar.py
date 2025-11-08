class NavbarBuilder:
    def __init__(self):
        self.items = []

    def add_item(self, name, link):
        self.items.append((name, link))

    def render(self):
        links = "".join([f'<a href="{l}">{n}</a> | ' for n, l in self.items])
        return f"<nav>{links}</nav>"