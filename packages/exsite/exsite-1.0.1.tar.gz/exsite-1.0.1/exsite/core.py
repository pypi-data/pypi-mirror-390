import os
from exsite.template import TemplateEngine
from exsite.router import Router
from exsite.form import FormBuilder
from exsite.project import ProjectManager
from exsite.navbar import NavbarBuilder

class Exsite:
    def __init__(self, project_name="MyWebsite"):
        self.project = ProjectManager(project_name)
        self.template = TemplateEngine(self.project.path)
        self.router = Router(self.project.path)
        self.form = FormBuilder(self.project.path)
        self.navbar = NavbarBuilder()
        self.css = self.CSSManager(self.project.path)
        self.js = self.JSManager(self.project.path)
        print(f"🚀 پروژه {project_name} آماده‌ست!")

    # --- ایجاد صفحه HTML
    def create_page(self, filename="index.html", title="EXSITE"):
        content = self.template.base_template(title)
        self.project.write_file(filename, content)
        print(f"✅ صفحه {filename} ساخته شد.")

    # --- اجرای پروژه (بدون نیاز به سرور)
    def run(self):
        download_path = os.path.join("/storage/emulated/0/Download", os.path.basename(self.project.path))
        try:
            os.system(f"cp -r {self.project.path} {download_path}")
            print(f"📂 پروژه در پوشه دانلود ذخیره شد: {download_path}")
        except Exception as e:
            print(f"⚠️ خطا در انتقال فایل‌ها: {e}")

    # --- مدیریت CSS
    class CSSManager:
        def __init__(self, path):
            self.path = path

        def create_css(self, filename="style.css", content=""):
            css_path = os.path.join(self.path, filename)
            with open(css_path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"🎨 فایل CSS ساخته شد: {filename}")

    # --- مدیریت JS
    class JSManager:
        def __init__(self, path):
            self.path = path

        def create_js(self, filename="script.js", content=""):
            js_path = os.path.join(self.path, filename)
            with open(js_path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"⚡ فایل JavaScript ساخته شد: {filename}")