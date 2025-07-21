from setuptools import setup, find_packages

setup(
    name="reconmaster",
    version="2.0.0",
    packages=find_packages(),
    install_requires=[
        "rich>=13.0",
        "pyyaml>=6.0",
        "aiohttp>=3.8",
        "psutil>=5.9"
    ],
    entry_points={
        "console_scripts": ["reconmaster=reconmaster.cli:main"]
    },
    package_data={
        "reconmaster": ["../configs/*.yaml"]
    },
    python_requires=">=3.8"
)