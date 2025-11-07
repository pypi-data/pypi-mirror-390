[![Documentation Status](https://readthedocs.org/projects/drive-ibd/badge/?version=latest)](https://drive-ibd.readthedocs.io/en/latest/?badge=latest)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![PyPI version](https://badge.fury.io/py/drive-ibd.svg)](https://badge.fury.io/py/drive-ibd)
[![DRIVE python package](https://github.com/belowlab/drive/actions/workflows/python-app.yml/badge.svg)](https://github.com/belowlab/drive/actions/workflows/python-app.yml)

# DRIVE

DRIVE (Distant Relatedness for Identification and Variant Evaluation) is a CLI tool that efficiently uses graph theory algorithms and IBD in large-scale cohorts to identify networks of individuals with shared haplotypes at a specified locus. These graph approaches allow for DRIVE to aggregate the pairwise shared IBD segments information into networks while retaining the identity of the pairwise segments. Additionally, when coupled with phenotype information, DRIVE can identify networks with enrichment of cases. This enrichment test can be used to prioritize networks and identify haplotypes that may be harboring potential rare variants of interest.

DRIVE utilizes common software design patterns to allow for adaptation into custom analytical pipelines and adoption into a variety of computational platforms, including cloud computing environments. To enable this adaptivity, DRIVE implements a plugin architecture so that the user can specify which plugins they wish to run and they can design their own plugins.

This tool was developed in Python by the Below Lab at Vanderbilt University. The documentation for how to use this tool can be found here [DRIVE documentation](https://drive-ibd.readthedocs.io/en/latest/)

## Notes on Installing DRIVE

Please read the following sections, "Python Versions" and "Checking the installed version" before installing DRIVE. Install instructions will begin in the section titled "PyPI Installation".

**Python Versions**:
DRIVE supports Python versions >=3.10 (but not Python version 3.11.0 specifically). The allowed python version can always be found in the pyproject.toml file under the section "requires-python". You can check your python version using the command 'python --version'. If your system python version is outside of the allowed range then you can either install an appropriate version from [Python.org](https://www.python.org/downloads/) or a package manager such as Homebrew on MacOS [Homebrew](https://brew.sh/), or [Conda](https://anaconda.org/anaconda/conda). *Additionally*, DRIVE does not support the multithreaded version of python that allows users to disable the GIL since there are still packages that are not yet compatible with this experimental version of python. You can check to see if this version is installed by running 'python --version'. If the result is python3.13t or python3.13t-dev then this is the incorrect version.

**Checking the installed version**:
After installing DRIVE You can check what version was installed using the following command in the environment in which you installed DRIVE. You can compare the version returned by this command to the version number indicated by the PYPI badge at the top of the README.md section or to the version listed in the pyproject.toml.

```bash
# If installed from PyPI
drive --version

# If installed using "pdm install"
pdm run drive --version

# if dependencies were installed using the conda .yml file or the pyproject.toml file with pip
python -m drive.drive --version

# if using the docker image
docker exec -it --rm drive --version drive-image-tag

# or using the signularity image
singularity exec singularity-drive-image.sif drive --version
```

You should see v3.0.2 (The project version is always listed in the pyproject.toml under the section "version" as well). If the version is older than 3.0 then something went wrong with the install (unless you intentionally installed an old version). Older versions of DRIVE before 3.0.0 will break the integrated testing framework because the command structure of the CLI was different. If you still wish to run the test with an older version then look at the section of the documentation called "Command to test legacy versions of DRIVE (before v3.0.0)". It is recommended that users always check the version number after installing DRIVE before they attempt to run any test data or their own data.

## Installing DRIVE

**PyPI Installation:**
DRIVE is available on PyPI and can easily be installed using the following command:

```bash
pip install drive-ibd
```

It is recommended to install DRIVE within a virtual environment such as venv, or conda. More information about this process can be found within the [documentation](https://drive-ibd.readthedocs.io/en/latest/index.html).

**Github Installation/Installing from source:**
If the user wishes to develop DRIVE or install the program from source then they can clone the repository. This process is described under the section called "Github Installation" in the documentation.

**Docker Installation:**
DRIVE is also available on Docker. This option eliminates the need for the user to worry about the Python Version. The docker image and the command to pull the image can be found here [jtb114/drive](https://hub.docker.com/r/jtb114/drive).

If you are working on an HPC cluster it may be better to use a singularity image. Singularity can pull the docker container and build a singularity image with the following command:

```bash
singularity pull singularity-image-name.sif docker://jtb114/drive:latest
```

**Running the Test Data:**
Once you have checked that the correct version of DRIVE is installed, you can run the test data to ensure that DRIVE is producing the expected output. To provide test data from DRIVE we simulated pairwise IBD segments using MSPrime, SHAPEIT4, and hap-IBD. This data is stored in the tests/test_inputs folder of the repository and is also bundled with the installs from PyPI or Docker. This data can be run using the commands below:

```bash
# If installed from PYPI
drive utilities test

# If installed using pdm
pdm run pytest -v tests/test_integration.py

# If dependencies were installed from the conda .yml file or the pyproject.toml file
python -m drive.drive utilities test

# If using Docker/Podman
docker run -it --rm drive-image-tag drive utilities test
```

Because singularity is a read-only file system for security, the commands to run the test data are different. Users can't run the built in testing framework because it will not have permissions to write to the filesystem (filesystem meaning the directory in the singularity image). Instead users can run the following commands to run the test data. First a writable "sandbox" has to be created. Users can replace the phrase "singularity-sandbox" with a name of their choosing. After that step, users can exec the sandbox. All other commands can use the normal singularity image (not the sandbox).

```bash
# Using singularity to make a sandbox
singularity build --sandbox singularity-sandbox singularity-image-path.sif
# Now you can run the unit test using the sandbox image
singularity exec -w --no-home singularity-sandox drive utilities test
```

*Note*: We expect only people who are contributing to DRIVE to be using PDM. The provided testing command for PDM allows us to ensure that the correct PDM virtual environment is being used. For this reason the PDM command is the most different from the others.

### Reporting issues

If you wish to report a bug or propose a feature you can find templates under the .github/ISSUE_TEMPLATE directory.
