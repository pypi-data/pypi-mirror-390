class JSBuilder:
    def __init__(self, path):
        self.path = path

    def create_js(self, filename="script.js", code=""):
        filepath = f"{self.path}/{filename}"
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(code)
        print(f"⚙️ فایل جاوااسکریپت {filename} ساخته شد.")