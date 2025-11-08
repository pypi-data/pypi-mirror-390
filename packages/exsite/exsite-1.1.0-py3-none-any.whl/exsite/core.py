import os
from datetime import datetime

class Exsite:
    def __init__(self, project_name):
        self.project_name = project_name
        self.pages = []
        self.css = CSSManager()
        self.js = JSManager()
        self.themes = ThemeManager()
        self.project_path = os.path.join(os.getcwd(), project_name)
        self.create_project_structure()

    def create_project_structure(self):
        """ایجاد پوشه‌های اصلی پروژه"""
        os.makedirs(self.project_path, exist_ok=True)
        os.makedirs(os.path.join(self.project_path, "assets"), exist_ok=True)
        os.makedirs(os.path.join(self.project_path, "assets", "images"), exist_ok=True)
        os.makedirs(os.path.join(self.project_path, "assets", "css"), exist_ok=True)
        os.makedirs(os.path.join(self.project_path, "assets", "js"), exist_ok=True)

    def create_page(self, filename, title="صفحه جدید", content=""):
        """ایجاد صفحه HTML جدید"""
        html_content = f"""<!DOCTYPE html>
<html lang="fa">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<link rel="stylesheet" href="assets/css/style.css">
<script src="assets/js/script.js"></script>
</head>
<body>
{content}
</body>
</html>"""
        path = os.path.join(self.project_path, filename)
        with open(path, "w", encoding="utf-8") as f:
            f.write(html_content)
        self.pages.append(filename)
        print(f"[+] صفحه {filename} ساخته شد.")

    def add_navbar(self, items):
        """ایجاد نوار ناوبری ساده"""
        nav_html = "<nav><ul>\n"
        for name, link in items:
            nav_html += f'  <li><a href="{link}">{name}</a></li>\n'
        nav_html += "</ul></nav>\n"
        return nav_html

    def add_card(self, title, content, image=None):
        """افزودن کارت طراحی زیبا"""
        img_tag = f'<img src="{image}" alt="{title}">' if image else ""
        return f"""
<div class="card">
  {img_tag}
  <h3>{title}</h3>
  <p>{content}</p>
</div>
"""

    def add_gallery(self, images):
        """گالری عکس ساده"""
        gallery = '<div class="gallery">\n'
        for img in images:
            gallery += f'  <img src="{img}" alt="gallery">\n'
        gallery += "</div>"
        return gallery

    def add_slider(self, images):
        """اسلایدر ساده با جاوااسکریپت"""
        imgs = "".join([f'<div class="slide"><img src="{i}"></div>' for i in images])
        slider_html = f"""
<div class="slider">
  {imgs}
</div>
<script>
let index = 0;
const slides = document.querySelectorAll('.slide');
function showSlide() {{
  slides.forEach((s, i) => {{
    s.style.display = i === index ? 'block' : 'none';
  }});
  index = (index + 1) % slides.length;
}}
setInterval(showSlide, 3000);
showSlide();
</script>
"""
        return slider_html

    def add_animation(self, name, css):
        """افزودن انیمیشن سفارشی"""
        anim_code = f"@keyframes {name} {{ {css} }}"
        self.css.add_rule(anim_code)

    def add_responsive(self):
        """افزودن طراحی واکنش‌گرا"""
        responsive = """
@media (max-width: 768px) {
  body { font-size: 14px; }
  nav ul { flex-direction: column; }
  .card { width: 100%; }
}
"""
        self.css.add_rule(responsive)

    def run(self):
        """اجرای محلی پروژه"""
        print(f"🌍 پروژه '{self.project_name}' آماده است.")
        print("📂 مسیر:", self.project_path)
        print("📅 ساخته‌شده در:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))


class CSSManager:
    def create_css(self, filename, content):
        path = os.path.join(os.getcwd(), "assets", "css")
        os.makedirs(path, exist_ok=True)
        with open(os.path.join(path, filename), "w", encoding="utf-8") as f:
            f.write(content)
        print(f"[CSS] فایل {filename} ساخته شد.")

    def add_rule(self, rule):
        path = os.path.join(os.getcwd(), "assets", "css", "style.css")
        with open(path, "a", encoding="utf-8") as f:
            f.write("\n" + rule + "\n")
        print("[+] قانون CSS جدید افزوده شد.")


class JSManager:
    def create_js(self, filename, content):
        path = os.path.join(os.getcwd(), "assets", "js")
        os.makedirs(path, exist_ok=True)
        with open(os.path.join(path, filename), "w", encoding="utf-8") as f:
            f.write(content)
        print(f"[JS] فایل {filename} ساخته شد.")


class ThemeManager:
    def __init__(self):
        self.active_theme = None
        self.themes = {
            "light": {"bg": "#ffffff", "text": "#000"},
            "dark": {"bg": "#121212", "text": "#fff"},
            "blue": {"bg": "#1e3a8a", "text": "#fff"}
        }

    def set_theme(self, name):
        if name not in self.themes:
            print(f"[!] تم '{name}' یافت نشد.")
            return
        theme = self.themes[name]
        css = f"body {{ background: {theme['bg']}; color: {theme['text']}; }}"
        path = os.path.join(os.getcwd(), "assets", "css", "style.css")
        with open(path, "a", encoding="utf-8") as f:
            f.write("\n" + css)
        self.active_theme = name
        print(f"[🎨] تم '{name}' فعال شد.")