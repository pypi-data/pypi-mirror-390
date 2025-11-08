import datetime

class TemplateEngine:
    def __init__(self, path):
        self.path = path

    def base_template(self, title="EXSITE", meta_desc="Built with exsite"):
        date = datetime.datetime.now().strftime("%Y-%m-%d")
        return f"""<!DOCTYPE html>
<html lang="fa">
<head>
    <meta charset="UTF-8">
    <meta name="description" content="{meta_desc}">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <nav>
        <a href="index.html">خانه</a> |
        <a href="about.html">درباره ما</a> |
        <a href="contact.html">تماس</a>
    </nav>
    <main>
        <h1>به {title} خوش آمدید!</h1>
        <p>تاریخ ساخت: {date}</p>
    </main>
    <script src="script.js"></script>
</body>
</html>"""	