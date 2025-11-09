from setuptools import setup, find_packages
from pathlib import Path

# with open("README.md", "r") as f:
#    description = f.read()


setup(
    name='ShellSteward',
    version='0.2.0',
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "shellsteward": ["data/commands.json"]
    },

    install_requires=[
        "typer[all]",
        "requests",
        "questionary",
        "rich",
        "pyperclip",
        "sentence-transformers",
        "faiss-cpu; platform_system != 'Windows'",
        "scikit-learn",
        "numpy",
        "httpx"
    ],
    entry_points={
    'console_scripts': [
        'shellsteward=shellsteward.cli:main',
    ],
    },
    license='MIT',
    author="Lucifer",
    description="ShellSteward: AI-powered CLI assistant for shell command generation and retrieval",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers",
        "Topic :: Utilities",
    ],
    python_requires=">=3.7",

    long_description = Path("README.md").read_text(encoding="utf-8"),

    long_description_content_type="text/markdown",
)