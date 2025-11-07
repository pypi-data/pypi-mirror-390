from setuptools import setup, find_packages
from pathlib import Path

this_dir = Path(__file__).parent
long_description = (this_dir / "README.md").read_text(encoding="utf-8")

setup(
    name="centrip-book",
    version='1.1.9',
    author="Centrip Studios",
    description="A command bookmarking tool for your terminal.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    py_modules=["centrip_book"],
    entry_points={"console_scripts": ["book=centrip_book:main"]},
    python_requires=">=3.6",
)
