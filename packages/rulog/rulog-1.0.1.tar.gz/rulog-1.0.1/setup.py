from setuptools import setup, find_packages

try:
    with open('README.md', encoding='utf-8') as f:
        long_description = f.read()
except FileNotFoundError:
    long_description = ''

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name='rulog',
    version='1.0.1',
    description=(
    "Rubika: A Python library for interacting with the Rubika Login APi. "
),

    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Mahdi Ahmadi',
    author_email='mahdiahmadi.1208@gmail.com',
    maintainer='Mahdi Ahmadi',
    maintainer_email='mahdiahmadi.1208@gmail.com',
    url='https://github.com/Mahdy-Ahmadi/rulog',
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: Communications :: Chat',
        'Topic :: Software Development :: Libraries',
        'Natural Language :: Persian',
    ],
    python_requires='>=3.6',
    install_requires=[
        "Pillow",
        'pycryptodome',
        'aiohttp',
        'httpx',
    ],
    keywords="rubika bot api library chat messaging rubpy pyrubi rubigram rubika_bot rubika_api fast_rub",
    project_urls={
        "Bug Tracker": "https://t.me/Bprogrammer",
        "Documentation": "https://github.com/Mahdy-Ahmadi/rulog/",
        "Source Code": "https://github.com/Mahdy-Ahmadi/rulog/tree/main/rulog",
    },
    license="MIT",
    zip_safe=False
)