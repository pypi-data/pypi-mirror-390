from pathlib import Path
from setuptools import setup, find_packages

here = Path(__file__).parent

# Import the package version without importing the package at runtime
try:
    from sneahi.version import __version__ as version  # type: ignore
except Exception:
    version = "0.0.0"

long_description = ""
readme_file = here / "readme.md"
if readme_file.exists():
    long_description = readme_file.read_text(encoding="utf-8")

setup(
    name="sneahi-multiplier",
    version=version,
    author="Sneahi Shah",
    author_email="sneahibshah@gmail.com",
    description="A small multiplier package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    include_package_data=True,
    python_requires=">=3.8",
    install_requires=["opencv-contrib-python"],
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
