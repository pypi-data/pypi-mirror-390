from setuptools import setup, find_packages

setup(
    name='exsite',
    version='1.0.0',
    author='Mamad Khatar',
    author_email='example@gmail.com',
    description='کتابخانه خفن جهانی ممد خطر 😎',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    url='https://pypi.org/project/exsite/',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)