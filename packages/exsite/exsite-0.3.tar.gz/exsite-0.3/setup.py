from setuptools import setup, find_packages

setup(
    name="exsite",  # نام پکیج همونی که می‌خوای جهانی بشه
    version="0.3",  # هر بار آپدیت می‌کنی اینو زیاد کن (مثلاً 0.4)
    author="TM HQ",  # اسم خودت 😎
    author_email="youremail@example.com",  # (ایمیل لازم نیست واقعی باشه ولی فرمتش درست باشه)
    description="A powerful Python library created by Mmd Hacker",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://pypi.org/project/exsite/",
    packages=find_packages(),
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)