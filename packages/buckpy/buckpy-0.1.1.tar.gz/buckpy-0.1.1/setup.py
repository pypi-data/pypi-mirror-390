'''
PyPi setup file.
'''

from pathlib import Path
from setuptools import setup, find_packages

# Safe long description load
readme_path = Path(__file__).parent / "README.md"
if readme_path.exists():
    long_description = readme_path.read_text(encoding="utf-8")
else:
    long_description = "BuckPy: Lateral buckling formation algorithm."

setup(
    name='buckpy',
    version='0.1.1',
    description='BuckPy: Lateral buckling formation algorithm',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='ismael-ripoll',
    url='https://github.com/Xodus-Group/BuckPy',
    project_urls={
        "Documentation": "https://buckpy-org.github.io/",
        "Source": "https://github.com/Xodus-Group/BuckPy",
        "Tracker": "https://github.com/Xodus-Group/BuckPy/issues",
    },
    packages=find_packages(include=['buckpy', 'buckpy.*']),
    package_data={"buckpy": ["_static/*"]},
    install_requires=[
        "matplotlib==3.8.3",
        "multiprocess==0.70.16",
        "numba==0.59.0",
        "numpy==1.26.4",
        "openpyxl==3.1.5",
        "pandas==2.2.1",
        "scipy==1.12.0",
        "xlrd==2.0.1",
        "XlsxWriter==3.2.0"
    ],
    entry_points={
        'console_scripts': [
            'buckpy=buckpy:run',
        ],
    },
    python_requires='>=3.11',
    include_package_data=True,
    license="GPL-3.0-or-later",
    classifiers=[
        'Programming Language :: Python :: 3',
        "Programming Language :: Python :: 3.11",
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
    ],
    keywords=["pipelines", "buckling", "engineering", "reliability", "simulation"],
)
