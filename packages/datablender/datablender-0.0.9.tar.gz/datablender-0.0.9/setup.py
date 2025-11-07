from sys import platform
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='datablender',
    version='0.0.9',
    description='Tools for data.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/MontrealMobilite/datablender.git',
    author='Julien Douville',
    packages=find_packages(),
    zip_safe=False,
    test_suite="tests",
    include_package_data=True,
    data_files=[
        (
            'datablender/postgresql/elements',
            [
                'datablender/postgresql/elements/column.sql',
                'datablender/postgresql/elements/constraint.sql',
                'datablender/postgresql/elements/database.sql',
                'datablender/postgresql/elements/extension.sql',
                'datablender/postgresql/elements/file.sql',
                'datablender/postgresql/elements/function.sql',
                'datablender/postgresql/elements/grant.sql',
                'datablender/postgresql/elements/index.sql',
                'datablender/postgresql/elements/partition.sql',
                'datablender/postgresql/elements/query.sql',
                'datablender/postgresql/elements/role.sql',
                'datablender/postgresql/elements/schema.sql',
                'datablender/postgresql/elements/table.sql',
                'datablender/postgresql/elements/view.sql',
            ]
        ),
        (
            'datablender/postgresql/queries',
            [
                'datablender/postgresql/queries/data_events_.sql',
                'datablender/postgresql/queries/main_files.sql'
            ]
        ),
    ],
    install_requires =[
        'unidecode',
        'aiohttp',
        'asyncpg',
        'sqlalchemy',
        'psycopg2' if platform == "win32" else 'psycopg2-binary',
        'datetime',
        'numpy',
        'pandas',
        'dbf',
        'openpyxl',
        'pyexcel',
        'xlrd',
        'beautifulsoup4',
        'selenium',
        'webdriver_manager',
        'postgis',
        'python-socketio',
        'dbfread',
        'scipy',
        'scikit-learn',
        'pyproj',
        'fiona',
        'geopandas',
        'dill',
        'pysmb',
        'aiosmb'
    ],
    extras_require={
        'dev': [
            'pytest',
            'build',
            'twine'
        ]
    }
)