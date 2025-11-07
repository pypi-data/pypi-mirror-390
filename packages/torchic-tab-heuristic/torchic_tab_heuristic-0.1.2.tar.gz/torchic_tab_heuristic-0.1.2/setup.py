from setuptools import setup, find_packages

with open("requirements.txt") as f:
    required = f.read().splitlines()

setup(
    name='torchic_tab_heuristic',
    version='0.1.2',
    packages=find_packages(),
    install_requires=required,
    author="Ioannis Dasoulas",
    author_email="ioannis.dasoulas@kuleuven.be",
    description="TorchicTab-Heuristic: Semantic Table Annotation with Wikidata",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/dtai-kg/TorchicTab-Heuristic",  
    license="Apache-2.0",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Natural Language :: English",
    ],
    python_requires='>=3.9, <3.12',
    #conda_deps=[],  # Path to your exported YAML file
)