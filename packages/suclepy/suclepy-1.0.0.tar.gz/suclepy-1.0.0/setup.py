from setuptools import setup, find_packages

setup(
    name="suclepy",
    version="1.0.0",
    author="Subodh Kumar Yadav",
    author_email="subodhkumary933@gmail.com",
    description="SUCLEPY — Smart Universal Cleaner Library for Python",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/subodhkryadav/suclepy",
    packages=find_packages(),
    include_package_data=True,
    python_requires=">=3.8",
    install_requires=[
        "pandas>=2.0",
        "numpy>=1.25",
        "tabulate>=0.9"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ],
    entry_points={
        "console_scripts": [
            "suclepy-cli = suclepy.cli.suclepy_cli:main"
        ]
    },
)
