from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="how-freedom-feels",
    version="0.1.7",
    author="Siddarth",
    author_email="sofiyasenthilkumar@gmail.com",
    description="A VPN connection manager with custom config support",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/guider23/how-freedom-feels",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.25.0",
        "click>=8.0.0",
    ],
    entry_points={
        "console_scripts": [
            "freedom=how_freedom_feels.cli:main",
        ],
    },
)
