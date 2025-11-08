from setuptools import setup, find_packages

setup(
    name="prcerlc",
    version="0.1.0",
    packages=find_packages(),
    install_requires=["requests>=2.28.0"],
    description="Python API wrapper for Emergency Response: Liberty County (PRC)",
    author="Gijs Ribberink",
    author_email="gijs.ribberink@kpnmail.nl",
    url="https://github.com/GijsRibberink/prcerlc",
    python_requires=">=3.8",
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
