from setuptools import setup, find_packages

# 📦 توضیحات نسخه فعلی
VERSION = "1.1.0"
DESCRIPTION = "EXSITE – ابزار ساخت سایت و اپ HTML با طراحی مدرن"
LONG_DESCRIPTION = """
🚀 EXSITE v1.1.0 – نسخه طراحی (Design Update)

EXSITE یک فریم‌ورک سبک و ساده برای ساخت صفحات HTML، CSS و JavaScript به‌صورت خودکار است.
مناسب برای طراحان، برنامه‌نویسان و کسانی که می‌خواهند به‌راحتی وب‌سایت بسازند.

ویژگی‌های نسخه 1.1.0:
- 🎨 سیستم تم‌ها (Themes)
- 🧱 ساخت کارت‌ها و گالری‌ها
- 🖼 ساخت اسلایدر تصاویر
- 💫 انیمیشن‌ساز ساده
- 📱 طراحی واکنش‌گرا (Responsive)
- ⚙️ پشتیبانی از ساختار خودکار پروژه
"""

setup(
    name="exsite",
    version=VERSION,
    author="EXL Team",
    author_email="exl.dev.team@gmail.com",
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    url="https://github.com/EXLTeam/exsite",
    packages=find_packages(),
    install_requires=[],  # وابستگی خاصی ندارد (می‌توانی بعدا اضافه کنی)
    keywords=[
        "html builder",
        "css generator",
        "website builder",
        "python web tool",
        "exsite"
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License",
        "Topic :: Software Development :: Code Generators",
        "Topic :: Internet :: WWW/HTTP :: Site Management",
    ],
    license="MIT",
    python_requires=">=3.6",
    include_package_data=True,
)