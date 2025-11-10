from setuptools import setup, find_packages

setup(
    name="Bohdan_drivers_report",  # унікальна назва на PyPI
    version="0.0.2",
    author="Your Name",
    author_email="your.email@example.com",
    description="Короткий опис пакета",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/mypackage",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)
