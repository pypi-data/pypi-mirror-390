from setuptools import setup, find_packages

setup(
    name="PySingletonMeta",
    version="0.1.0.3",            
    author="Armen-Jean Andreasian",
    author_email="armen.andreasian.dev@proton.me",
    description="Singleton Metaclass for comfy imports",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/a-jean-andreasian/Lambda-REST-Client",
    packages=find_packages(exclude=["tests", "docs"]),
    python_requires=">=3.8",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    include_package_data=True,
)
