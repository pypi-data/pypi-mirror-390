from setuptools import setup

setup(
    name="centrip-book",
    version="1.0.2",
    py_modules=["centrip_book"],
    entry_points={"console_scripts": ["book=centrip_book:main"]},
    author="Michael Sowerwine",
    author_email="you@example.com",
    description="A simple cross-system command bookmarking tool for your terminal.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/centrip-book",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS",
    ],
    python_requires=">=3.6",
)
