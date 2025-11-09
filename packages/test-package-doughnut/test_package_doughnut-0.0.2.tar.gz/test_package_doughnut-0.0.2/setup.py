from setuptools import setup

setup(
    name="test-package-doughnut",
    version="0.0.2",
    description="A test package to verify twine configuration",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="doughnut",
    author_email="test@example.com",
    py_modules=[],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
    ],
)