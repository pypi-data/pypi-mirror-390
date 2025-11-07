import os

class ProjectManager:
    def __init__(self, name):
        self.name = name
        self.path = os.path.join(os.getcwd(), name)
        self.create_structure()

    def create_structure(self):
        os.makedirs(self.path, exist_ok=True)
        print(f"📁 مسیر پروژه ساخته شد: {self.path}")

    def write_file(self, filename, content):
        with open(os.path.join(self.path, filename), "w", encoding="utf-8") as f:
            f.write(content)
        print(f"📄 فایل {filename} ذخیره شد.")