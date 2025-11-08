import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="h5_info_pkg_inra_phenome",
    version="1.3.4",
    author="Eric David",
    author_email="eric.david@ephesia-consult.com",
    description="Utility package for extracting, reading and saving metadata from HDF5 Phenomobile V2, Phenoverger and LITERAL acquisition files",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://forgemia.inra.fr/4p/tools/h5info",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
    install_requires=[
        'h5py',
        'Pillow'
    ]
)
