# Met-A-Cell

# Content
- [Overview](#overview)
- [Documentation](#documentation)
- [System Requirements](#system-requirements)
- [Installation Guide](#installation-guide)
- [Tutorials](#tutorials)
- [License](#license)
- [References](#references)
- [tissue](https://github.com/TsinghuaMetabolism/Met-A-Cell/issues)

# Overview
Met-A-Cell is a scalable python package for analyzing single-cell metabolomics (SCM) built jointly with anndata. It supports comprehensive single-cell data analysis, offering key functionalities including:
1) Baseline correction and background noise removal;
2) Identification of single-cell events;
3) Annotation of multi-cell events;
4) Extraction and annotation of single-cell metabolic features; 
5) Alignment of LIF and MS data;
6) Downstream analysis such as clustering, dimensionality reduction analysis, differential metabolite analysis, and pathway enrichment analysis.

# Documentation
For detailed documentation and usage examples, please refer to the following:
- [Met-A-Cell Tutorial]()
- [API Documentation]()
- [FAQ]()

# System Requirements
## Hardware Requirements
`Met-A-Cell` package requires only a standard computer with enough RAM to support in-memory operations. 
## Software Requirements
This package is supported for macOS and Linux. The package has been tested on the following systems:
- macOS: Sonoma (14.6.1)
- Linux: CentOS (7.9.2009)

The package have also tested on Google Colab, with the runtime type set to Python3, hardware accelerator to CPU, and High-RAM mode enabled.

## Python Dependencies
**Python version**: 3.9.10 or higher.

`Met-A-Cell` requires the following:
- numpy>=1.26.4
- pandas>=2.1.0
- scipy>=1.11.4
- tqdm>=4.62.3
- pyopenms>=2.7.0 
- pybaselines>=1.1.0 
- matplotlib>=3.7.3 
- anndata>=0.10.8
- scanpy>=1.10.2

# Installation Guide
## Install from Github
```angular2html
git clone https://github.com/TsinghuaMetabolism/Met-A-Cell.git
cd metacell
python3 setup.py install
```

# Tutorials
For a quick introduction to Met-A-Cell, we provide a concise tutorial along with raw SCM example files to demonstrate the application of the package. For a comprehensive description of its features, please refer to the documentation with usage: [Met-A-Cell Tutorial]().

# License
`Met-A-Cell` is licensed under the MIT License. Feel free to use, modify, and distribute the software, but please refer to the full license for more details.
# References
This software was developed based on the following research:
1. anndata: Annotated data. Isaac Virshup, Sergei Rybakov, Fabian J. Theis, Philipp Angerer, F. Alexander Wolf. JOSS 2024 Sep 16. doi: [10.21105/joss.04371](https://doi.org/10.21105/joss.04371).
2. The scverse project provides a computational ecosystem for single-cell omics data analysis. Isaac Virshup, Danila Bredikhin, Lukas Heumos, Giovanni Palla, Gregor Sturm, Adam Gayoso, Ilia Kats, Mikaela Koutrouli, Scverse Community, Bonnie Berger, Dana Pe’er, Aviv Regev, Sarah A. Teichmann, Francesca Finotello, F. Alexander Wolf, Nir Yosef, Oliver Stegle & Fabian J. Theis. Nat Biotechnol. 2023 Apr 10. doi: [10.1038/s41587-023-01733-8](https://doi.org/10.1038/s41587-023-01733-8).
3. SCANPY: large-scale single-cell gene expression data analysis. F. Alexander Wolf, Philipp Angerer, Fabian J. Theis. Genome Biology 2018 Feb 06. doi: [10.1186/s13059-017-1382-0](https://doi.org/10.1186/s13059-017-1382-0).