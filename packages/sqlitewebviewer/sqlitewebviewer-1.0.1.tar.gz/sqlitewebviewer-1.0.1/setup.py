from setuptools import setup, find_packages
from pathlib import Path

README = (Path(__file__).parent / "README.md").read_text(encoding="utf-8")

setup(
    name="sqlitewebviewer",
    version="1.0.1",
    description="A web-based SQLite browser and query tool",
    long_description=README,
    long_description_content_type="text/markdown",
    author="Mandeep Cheema",
    author_email="",
    url="https://github.com/mandeepcheema/sqlitewebviewer",
    project_urls={
        "Source": "https://github.com/mandeepcheema/sqlitewebviewer",
        "Issues": "https://github.com/mandeepcheema/sqlitewebviewer/issues",
    },
    license="MIT",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "Flask>=2.2",
    ],
    python_requires=">=3.8",
    entry_points={
        'console_scripts': [
            'sqlitewebviewer = sqlitewebviewer.app:main',
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Framework :: Flask",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "Topic :: Database",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Operating System :: OS Independent",
    ],
)

