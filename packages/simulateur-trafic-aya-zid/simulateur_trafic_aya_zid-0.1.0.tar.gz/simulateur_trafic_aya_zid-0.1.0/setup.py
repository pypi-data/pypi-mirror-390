from setuptools import setup, find_packages

setup(
    name="simulateur-trafic-aya-zid",
    version="1.0.0",
    description="Simulateur de trafic routier intelligent avec modélisation de réseaux",
    author="Aya Zid",
    author_email="azid28278@gmail.com",
    license="MIT",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "numpy>=2.3.4,<3.0.0",
        "pandas>=2.3.3,<3.0.0",
        "matplotlib>=3.10.7,<4.0.0",
        "seaborn>=0.13.2,<0.14.0",
        "openpyxl>=3.1.5,<4.0.0",
        "tqdm>=4.67.1,<5.0.0",
        "python-dateutil>=2.9.0.post0,<3.0.0",
    ],
)
