from setuptools import setup, find_packages
from pathlib import Path

README = Path("README.md").read_text(encoding="utf-8")

setup(
    name="kashima",
    version="1.3.3",
    author="Alejandro Verri Kozlowski",
    author_email="averri@fi.uba.ar",
    description="Machine Learning Tools for Geotechnical Earthquake Engineering.",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/SRKConsulting/kashima",
    packages=find_packages(
        include=["kashima*"],
        exclude=("dist*", "build*", "tests*", "test*", "legacy*", "archive*"),
    ),
    include_package_data=True,
    install_requires=[
        "pandas>=1.3.0",
        "numpy>=1.20.0",
        "folium>=0.12.0",
        "geopandas>=0.10.0",
        "pyproj>=3.0.0",
        "requests>=2.25.0",
        "branca>=0.4.0",
        "geopy>=2.0.0",
        "matplotlib>=3.3.0",
        "obspy>=1.2.0",
        "appdirs>=1.4.0",
        "pyarrow>=10.0.0",  # Required for parquet cache support
    ],
    entry_points={
        "console_scripts": [
            # No console scripts currently defined
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    package_data={
        "kashima.mapper": ["data/*.csv", "data/*.geojson"],
    },
)
