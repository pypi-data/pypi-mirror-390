import os
from setuptools import setup, find_packages

#taken from pip/setup.py
def read(rel_path: str) -> str:
    here = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(here, rel_path)) as fp:
        return fp.read()


def get_version(rel_path: str) -> str:
    for line in read(rel_path).splitlines():
        if line.startswith("__version__"):
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]
    raise RuntimeError("Unable to find version string.")

setup(
    name='Xurpas Data Quality Report',
    version=get_version("src/xurpas_data_quality/__init__.py"),
    packages = find_packages(
        where='src',
        include=['xurpas_data_quality.*']),
    package_dir={"":"src"},
    package_data={
        'xurpas_data_quality': ["py.typed"]
    },
    include_package_data=True,
    author='Neil Ortaliz',
    author_email='neillaurenceortaliz@gmail.com',
    description='XAIL Data quality',
    install_requires=[
        'visions',
        'pandas',
        'numpy',
        'matplotlib',
        'jinja2',
        'openpyxl',
        'pyarrow',
        'pytest',
        'minify_html',
        'wordcloud',
        'pydantic-settings',
        'pyspark',
        'pyyaml'
    ]
)