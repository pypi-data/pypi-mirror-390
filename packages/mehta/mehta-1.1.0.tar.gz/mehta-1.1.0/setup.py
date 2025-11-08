from setuptools import setup, find_packages

setup(
    name="mehta",
    version="1.1.0",
    author="Ankit Mehta",
    author_email="starexx.m@gmail.com",
    description="A telegram SDK with clean and beginner-friendly command decorators.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        "pyTeleBot",
        "telethon",
        "requests"
    ],
    entry_points={
        'console_scripts': [
            'mehta=mehta:main',
        ],
    },
)