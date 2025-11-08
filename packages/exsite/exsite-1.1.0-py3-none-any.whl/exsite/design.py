import os

class DesignSystem:
    def __init__(self, project_path):
        self.project_path = project_path

    def auto_page(self, filename="index.html", title="صفحه خودکار"):
        content = f"""
<!DOCTYPE html>
<html lang="fa">
<head>
<meta charset="UTF-8">
<title>{title}</title>
<link rel="stylesheet" href="style.css">
</head>
<body>
<header><h1>{title}</h1></header>
<main><p>این صفحه به‌صورت خودکار با EXSITE ساخته شده است!</p></main>
<footer><small>© 2025 EXSITE</small></footer>
</body>
</html>
"""
        path = os.path.join(self.project_path, filename)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"[✅] صفحه خودکار ساخته شد: {filename}")

    def add_theme(self, theme_name="light"):
        css_path = os.path.join(self.project_path, "style.css")
        themes = {
            "light": "body { background:#fff; color:#333; }",
            "dark": "body { background:#111; color:#eee; }",
            "blue": "body { background:#007BFF; color:#fff; }"
        }
        css = themes.get(theme_name, themes["light"])
        with open(css_path, "a", encoding="utf-8") as f:
            f.write("\n" + css)
        print(f"[🎨] تم '{theme_name}' اضافه شد")

    def add_fonts_and_colors(self, font="sans-serif", color="#333"):
        css_path = os.path.join(self.project_path, "style.css")
        css = f"body {{ font-family:{font}; color:{color}; }}"
        with open(css_path, "a", encoding="utf-8") as f:
            f.write("\n" + css)
        print(f"[🖋️] فونت و رنگ اضافه شد")

    def create_gallery(self, images):
        gallery_html = "<div class='gallery'>\n"
        for img in images:
            gallery_html += f"<img src='{img}' alt='Gallery Image'>\n"
        gallery_html += "</div>"
        return gallery_html

    def create_slider(self, images):
        slider_html = "<div class='slider'>\n"
        for img in images:
            slider_html += f"<div class='slide'><img src='{img}'></div>\n"
        slider_html += "</div>"
        return slider_html

    def add_responsive(self):
        css_path = os.path.join(self.project_path, "style.css")
        responsive_css = """
@media (max-width:768px) {
  body { font-size: 14px; }
  img { width: 100%; height: auto; }
}
"""
        with open(css_path, "a", encoding="utf-8") as f:
            f.write("\n" + responsive_css)
        print("[📱] طراحی واکنش‌گرا فعال شد")

    def create_card(self, title, text):
        return f"<div class='card'><h3>{title}</h3><p>{text}</p></div>"

    def add_button(self, label="کلیک کنید", link="#"):
        return f"<a href='{link}' class='btn'>{label}</a>"

    def add_css_effects(self):
        css_path = os.path.join(self.project_path, "style.css")
        effects = """
.btn {
  padding: 10px 20px;
  background: linear-gradient(45deg, #00c6ff, #0072ff);
  color: white;
  border-radius: 8px;
  text-decoration: none;
  transition: 0.3s;
}
.btn:hover {
  transform: scale(1.05);
}
"""
        with open(css_path, "a", encoding="utf-8") as f:
            f.write("\n" + effects)
        print("[💫] افکت‌های CSS اضافه شد")

    def add_animation(self):
        css_path = os.path.join(self.project_path, "style.css")
        animation_css = """
@keyframes fadeIn {
  from {opacity: 0;}
  to {opacity: 1;}
}
.fade-in {
  animation: fadeIn 1.2s ease-in;
}
"""
        with open(css_path, "a", encoding="utf-8") as f:
            f.write("\n" + animation_css)
        print("[🎬] انیمیشن‌ساز ساده فعال شد")