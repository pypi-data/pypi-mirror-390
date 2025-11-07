from setuptools import setup

setup(
    name="centrip-book",
    version='1.0.7',
    py_modules=["centrip_book"],
    entry_points={"console_scripts": ["book=centrip_book:main"]},
    author="Michael Sowerwine",
    author_email="you@example.com",
    license="MIT",
    description="A simple cross-system command bookmarking tool for your terminal.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS",
    ],
    python_requires=">=3.6",
)
