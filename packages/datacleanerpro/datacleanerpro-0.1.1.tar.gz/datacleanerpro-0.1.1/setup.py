from setuptools import setup, find_packages

setup(
    name="datacleanerpro",
    version="0.1.1",
    author="Nabiya Inamdar",
    author_email="nabiya.inamdar@example.com",  # TODO: Update with your real email
    description="A simple and efficient data cleaning library for CSV files.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/datacleanerpro",  # TODO: Update with your repo URL
    project_urls={
        "Bug Tracker": "https://github.com/yourusername/datacleanerpro/issues",
        "Documentation": "https://github.com/yourusername/datacleanerpro#readme",
        "Source Code": "https://github.com/yourusername/datacleanerpro",
    },
    packages=find_packages(),
    install_requires=["pandas"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    keywords="data cleaning, csv, pandas, data processing",
)
