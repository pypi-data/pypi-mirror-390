class HTMLBuilder:
    def __init__(self, path):
        self.path = path

    def create_tag(self, tag, content="", **attrs):
        attr_str = " ".join(f'{k}="{v}"' for k, v in attrs.items())
        return f"<{tag} {attr_str}>{content}</{tag}>"

    def add_to_page(self, filename, content):
        filepath = f"{self.path}/{filename}"
        with open(filepath, "a", encoding="utf-8") as f:
            f.write("\n" + content)
        print(f"🧱 تگ جدید به {filename} اضافه شد.")