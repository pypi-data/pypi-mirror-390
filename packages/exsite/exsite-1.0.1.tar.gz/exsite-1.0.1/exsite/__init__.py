# __init__.py -- Python EXL v0.3 (Advanced)
import os
import random
import string
import json
import shutil
import traceback
import hashlib
import zipfile
import time

__version__ = "0.3"
__name__ = "Python EXL"

# مسیر پوشه دانلود در اندروید (معمولاً)
DOWNLOAD_PATH = "/storage/emulated/0/Download"

# ----------------------------------------
# سیستم ماژولار (فهرست برای مستندات)
# ----------------------------------------
modules = {
    "core": ["random_number", "random_password"],
    "web": ["WebPage", "make_site", "default_template"],
    "ai": ["ai_designer"],
    "system": ["export_site_info", "docs"],
    "advanced": ["Database", "Router", "Cache", "Security", "AutoTester", "easy_deploy"]
}

# ----------------------------------------
# خطایابی پیشرفته (Decorator)
# ----------------------------------------
def debug_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print("❌ خطا در اجرای تابع:", func.__name__)
            print("📄 توضیحات:", str(e))
            # آخرین خط استک ترک را چاپ کن (کوتاه)
            tb = traceback.format_exc().splitlines()
            if tb:
                print("📘 مسیر خطا:", tb[-1])
            return None
    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    return wrapper

# ----------------------------------------
# معرفی و تست
# ----------------------------------------
def test():
    print(f"✅ Python EXL v{__version__} آماده به کار است!")
    print("📦 ویژگی‌ها: ساخت سایت، قالب آماده، دیتابیس، کش، امنیت، تست خودکار، دپلوی آسان و مستندات خودکار.\n")

# ----------------------------------------
# ابزارهای پایه
# ----------------------------------------
@debug_error
def random_number(min_val=0, max_val=100):
    """تولید عدد تصادفی"""
    num = random.randint(min_val, max_val)
    print(f"🎲 عدد تصادفی: {num}")
    return num

@debug_error
def random_password(length=8):
    """تولید رمز تصادفی"""
    chars = string.ascii_letters + string.digits + "!@#$%^&*()"
    password = ''.join(random.choice(chars) for _ in range(length))
    print(f"🔑 رمز تصادفی: {password}")
    return password

# ----------------------------------------
# وب: صفحات HTML
# ----------------------------------------
class WebPage:
    """کلاس ساده برای ساخت صفحات HTML"""
    def __init__(self, title="صفحه جدید EXL"):
        self.title = title
        self.body = ""
        print(f"🧱 ساخت صفحه جدید با عنوان: {title}")

    def add(self, html):
        """افزودن HTML به بدنه صفحه"""
        self.body += str(html) + "\n"

    @debug_error
    def save(self, filename="index.html"):
        """
        ذخیره صفحه: می‌نویسد در پوشه پروژه موقت و سپس منتقل می‌کند به Downloads
        """
        # مسیر موقت داخل فضای پروژه Pydroid
        tmp_dir = "/storage/emulated/0/Pydroid3/projects"
        try:
            os.makedirs(tmp_dir, exist_ok=True)
        except Exception:
            pass
        temp_path = os.path.join(tmp_dir, filename)

        content = f"""<!DOCTYPE html>
<html lang="fa">
<head>
<meta charset='utf-8'>
<title>{self.title}</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
body {{
    font-family: sans-serif;
    text-align: center;
    background: #fafafa;
    color: #333;
    margin: 0;
    padding: 20px;
}}
.container {{ max-width:900px; margin: 0 auto; padding: 20px; }}
h1 {{ color: #2196f3; margin-bottom: 10px; }}
footer {{ color: gray; font-size: 13px; margin-top: 30px; }}
</style>
</head>
<body>
<div class="container">
{self.body}
</div>
<footer>ساخته شده با ❤️ Python EXL</footer>
</body>
</html>"""

        # نوشتن فایل موقت
        with open(temp_path, "w", encoding="utf-8") as f:
            f.write(content)

        # انتقال به پوشه دانلود
        final_path = os.path.join(DOWNLOAD_PATH, filename)
        try:
            # اگر فایل مقصد موجود بود، آن را بازنویسی کن
            if os.path.exists(final_path):
                os.remove(final_path)
            shutil.move(temp_path, final_path)
        except Exception as e:
            # اگر انتقال ناموفق بود، تلاش برای کپی مستقیم
            try:
                shutil.copy(temp_path, final_path)
                os.remove(temp_path)
            except Exception as e2:
                print("❌ خطا در انتقال فایل به Downloads:", e2)
                raise

        print(f"✅ سایت ساخته شد و در پوشه دانلود ذخیره گردید:")
        print(f"📂 مسیر: {final_path}")
        print("🌐 حالا می‌تونی فایل HTML رو باز کنی و سایتت رو ببینی!")

# ----------------------------------------
# هوش مصنوعی ساده (تولید المان‌ها)
# ----------------------------------------
@debug_error
def ai_designer(prompt):
    """تولید ساده HTML بر اساس متن"""
    print(f"🧠 طراحی خودکار برای: {prompt}")
    p = prompt.lower()
    if "فرم" in p or "ورود" in p:
        return "<form><input placeholder='نام کاربری'><br><input type='password' placeholder='رمز عبور'><br><button>ورود</button></form>"
    if "کارت" in p or "card" in p:
        return "<div style='border:1px solid #ddd;padding:12px;border-radius:8px;display:inline-block;'>🌟 کارت نمونه</div>"
    if "دکمه" in p or "button" in p:
        return "<button style='padding:10px 16px;border-radius:6px;'>دکمه</button>"
    if "متن" in p or "paragraph" in p:
        return f"<p>{prompt}</p>"
    if "عکس" in p or "image" in p:
        return "<img src='https://via.placeholder.com/320x180' alt='image' style='max-width:100%;border-radius:8px;'>"
    # fallback
    return f"<p style='color:gray'>🔹 توضیح: {prompt}</p>"

# ----------------------------------------
# قالب آماده
# ----------------------------------------
def default_template(title, body):
    """قالب پیش‌فرض HTML"""
    return f"""
<html>
<head><meta charset='utf-8'><title>{title}</title></head>
<body style="font-family:sans-serif;text-align:center;background:#f8f9fa;margin:0;padding:20px;">
    <div style="max-width:900px;margin:0 auto;">
        <h1 style="color:#007BFF;">🌐 {title}</h1>
        <div style="margin:20px auto;">{body}</div>
        <footer style="color:#666;font-size:13px;">ساخته شده با Python EXL 🐍</footer>
    </div>
</body>
</html>
"""

@debug_error
def make_site(title, content):
    """ساخت سریع سایت با قالب آماده و ذخیره در Downloads"""
    print(f"⚡ ساخت سریع سایت با عنوان: {title}")
    page = WebPage(title)
    html_ready = default_template(title, content)
    page.add(html_ready)
    page.save("site_exl.html")

# ----------------------------------------
# ذخیره اطلاعات سایت به JSON (برای توسعه)
# ----------------------------------------
@debug_error
def export_site_info(title, filename="site_info.json"):
    info = {
        "title": title,
        "version": __version__,
        "author": "Python EXL",
        "modules": list(modules.keys()),
        "generated_at": int(time.time())
    }
    path = os.path.join(DOWNLOAD_PATH, filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(info, f, ensure_ascii=False, indent=4)
    print(f"🗂 فایل اطلاعات سایت ساخته شد: {path}")

# ----------------------------------------
# دیتابیس ساده بر پایه JSON
# ----------------------------------------
class Database:
    """Database ذخیره شده در فایل JSON داخل Downloads"""
    def __init__(self, name="exl_data.json"):
        self.path = os.path.join(DOWNLOAD_PATH, name)
        # اگر فایل وجود ندارد، بساز
        if not os.path.exists(self.path):
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump({}, f)
        print(f"🗂 دیتابیس آماده است: {self.path}")

    @debug_error
    def save(self, key, value):
        with open(self.path, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except Exception:
                data = {}
        data[key] = value
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"💾 داده ذخیره شد: {key} → {value}")

    @debug_error
    def get(self, key):
        with open(self.path, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except Exception:
                data = {}
        return data.get(key, None)

# ----------------------------------------
# مسیریابی ساده (Router)
# ----------------------------------------
class Router:
    """Router برای نگاشت path به توابع (اجرای محلی)"""
    def __init__(self):
        self.routes = {}

    def add(self, path, func):
        self.routes[path] = func
        print(f"🛣 مسیر '{path}' اضافه شد.")

    def run(self, path):
        if path in self.routes:
            print(f"🚀 اجرای مسیر '{path}' ...")
            try:
                self.routes[path]()
            except Exception as e:
                print("❌ خطا در اجرای مسیر:", e)
        else:
            print(f"❌ مسیر '{path}' یافت نشد!")

# ----------------------------------------
# کش ساده در حافظه
# ----------------------------------------
class Cache:
    cache_data = {}

    @staticmethod
    def save(key, value):
        Cache.cache_data[key] = value
        print(f"🗄 کش ذخیره شد: {key}")

    @staticmethod
    def get(key):
        return Cache.cache_data.get(key, None)

    @staticmethod
    def clear():
        Cache.cache_data.clear()
        print("🗄 کش پاک شد")

# ----------------------------------------
# امنیت داخلی (هش)
# ----------------------------------------
class Security:
    @staticmethod
    def hash_text(text):
        h = hashlib.sha256(text.encode()).hexdigest()
        print(f"🔒 هش ساخته شد: {h[:20]}...")
        return h

    @staticmethod
    def check_hash(text, hashed):
        return hashlib.sha256(text.encode()).hexdigest() == hashed

# ----------------------------------------
# تست خودکار
# ----------------------------------------
class AutoTester:
    @staticmethod
    def run_all():
        print("🧪 شروع تست خودکار...")
        try:
            random_number()
            random_password()
            db = Database()
            db.save("test_key", "ok")
            got = db.get("test_key")
            if got == "ok":
                print("✅ تمام تست‌ها با موفقیت اجرا شدند!")
            else:
                print("❌ تست دیتابیس ناموفق بود.")
        except Exception as e:
            print("❌ خطا در تست:", e)

# ----------------------------------------
# دپلوی آسان (فشرده‌سازی پروژه)
# ----------------------------------------
@debug_error
def easy_deploy(project_path, output_name="site_exl.zip"):
    """
    فشرده‌سازی یک پوشه پروژه و ذخیره ZIP در پوشه Downloads
    """
    if not os.path.exists(project_path):
        raise FileNotFoundError("پوشه پروژه وجود ندارد: " + project_path)
    zip_path = os.path.join(DOWNLOAD_PATH, output_name)
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(project_path):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, project_path)
                zipf.write(file_path, arcname)
    print(f"📦 دپلوی انجام شد! فایل ZIP در Downloads ذخیره شد:\n{zip_path}")

# ----------------------------------------
# مستندات خودکار
# ----------------------------------------
def docs():
    print("📘 مستندات خودکار Python EXL")
    print("─────────────────────────────")
    for cat, funcs in modules.items():
        print(f"\n🔹 {cat.upper()}:")
        for f in funcs:
            print(f"   • {f}")
    print("\n💡 نسخه:", __version__)
    print("🐍 توسعه‌دهنده: Python EXL Project\n")