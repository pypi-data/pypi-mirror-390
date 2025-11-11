from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="mehta",
    version="1.1.5",
    author="Ankit Mehta",
    author_email="starexx.m@gmail.com",
    description="A beginner-friendly telegram sdk providing intuitive command decorators.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: Information Technology",
        "Topic :: Communications :: Chat",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    keywords=(
        "telegram bot sdk framework telethon pyTelegramBotAPI telebot "
        "bot-development decorator message-handling automation"
    ),
    python_requires=">=3.7",
    install_requires=[
        "pyTeleBot>=0.1.0",
        "telethon>=1.30.0",
        "requests>=2.25.0",
    ],
    extras_require={
        "dev": ["pytest", "black", "flake8"],
        "docs": ["sphinx", "sphinx-rtd-theme"],
    },
    entry_points={
        "console_scripts": [
            "mehta=mehta:main",
        ],
    },
    maintainer="Ankit Mehta",
    maintainer_email="starexx.m@gmail.com",
    platforms=["any"],
    project_name="Mehta",
    project_description=(
        "A decorator-based SDK for building Telegram bots "
        "with clean syntax, modular structure, and powerful features."
    ),
    project_keywords=[
        "telegram",
        "bot",
        "sdk",
        "telethon",
        "decorator",
        "framework",
    ],
)