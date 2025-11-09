from setuptools import setup, find_packages
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="nasa-admin-cli",
    version="0.1.0",
    author="Ashlesh Deshmukh",
    author_email="youremail@example.com",
    description="CLI tool for NASA admin tasks",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/nasa-admin-cli",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "pwinput",
    ],
    include_package_data=True,  # include JSON files via MANIFEST.in
    entry_points={
        "console_scripts": [
            "nasa-admin-cli=nasa_admin_cli.main:main",  # links CLI command to main()
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
