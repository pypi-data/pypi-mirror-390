|Icon| |title|_
===============

.. |title| replace:: diffpy.distanceprinter
.. _title: https://diffpy.github.io/diffpy.distanceprinter

.. |Icon| image:: https://avatars.githubusercontent.com/diffpy
        :target: https://diffpy.github.io/diffpy.distanceprinter
        :height: 100px

|PyPI| |Forge| |PythonVersion| |PR|

|CI| |Codecov| |Black| |Tracking|

.. |Black| image:: https://img.shields.io/badge/code_style-black-black
        :target: https://github.com/psf/black

.. |CI| image:: https://github.com/diffpy/diffpy.distanceprinter/actions/workflows/matrix-and-codecov-on-merge-to-main.yml/badge.svg
        :target: https://github.com/diffpy/diffpy.distanceprinter/actions/workflows/matrix-and-codecov-on-merge-to-main.yml

.. |Codecov| image:: https://codecov.io/gh/diffpy/diffpy.distanceprinter/branch/main/graph/badge.svg
        :target: https://codecov.io/gh/diffpy/diffpy.distanceprinter

.. |Forge| image:: https://img.shields.io/conda/vn/conda-forge/diffpy.distanceprinter
        :target: https://anaconda.org/conda-forge/diffpy.distanceprinter

.. |PR| image:: https://img.shields.io/badge/PR-Welcome-29ab47ff
        :target: https://github.com/diffpy/diffpy.distanceprinter/pulls

.. |PyPI| image:: https://img.shields.io/pypi/v/diffpy.distanceprinter
        :target: https://pypi.org/project/diffpy.distanceprinter/

.. |PythonVersion| image:: https://img.shields.io/pypi/pyversions/diffpy.distanceprinter
        :target: https://pypi.org/project/diffpy.distanceprinter/

.. |Tracking| image:: https://img.shields.io/badge/issue_tracking-github-blue
        :target: https://github.com/diffpy/diffpy.distanceprinter/issues

Distance Printer, calculate the inter atomic distances. Part of xPDFsuite

Citation
--------

If you use diffpy.distanceprinter in a scientific publication, we would like you to cite this package as

        Xiaohao Yang, Pavol Juhas, Christopher L. Farrow and Simon J. L. Billinge, xPDFsuite: an end-to-end
        software solution for high throughput pair distribution function transformation, visualization and
        analysis, arXiv 1402.3163 (2025)

Installation
------------

The preferred method is to use `Miniconda Python
<https://docs.conda.io/projects/miniconda/en/latest/miniconda-install.html>`_
and install from the "conda-forge" channel of Conda packages.

To add "conda-forge" to the conda channels, run the following in a terminal. ::

        conda config --add channels conda-forge

We want to install our packages in a suitable conda environment.
The following creates and activates a new environment named ``diffpy.distanceprinter_env`` ::

        conda create -n diffpy.distanceprinter_env diffpy.distanceprinter
        conda activate diffpy.distanceprinter_env

The output should print the latest version displayed on the badges above.

If the above does not work, you can use ``pip`` to download and install the latest release from
`Python Package Index <https://pypi.python.org>`_.
To install using ``pip`` into your ``diffpy.distanceprinter_env`` environment, type ::

        pip install diffpy.distanceprinter

If you prefer to install from sources, after installing the dependencies, obtain the source archive from
`GitHub <https://github.com/diffpy/diffpy.distanceprinter/>`_. Once installed, ``cd`` into your ``diffpy.distanceprinter`` directory
and run the following ::

        pip install .

This package also provides command-line utilities. To check the software has been installed correctly, type ::

        diffpy.distanceprinter --version

You can also type the following command to verify the installation. ::

        python -c "import diffpy.distanceprinter; print(diffpy.distanceprinter.__version__)"


To view the basic usage and available commands, type ::

        diffpy.distanceprinter -h

Support and Contribute
----------------------

If you see a bug or want to request a feature, please `report it as an issue <https://github.com/diffpy/diffpy.distanceprinter/issues>`_ and/or `submit a fix as a PR <https://github.com/diffpy/diffpy.distanceprinter/pulls>`_.

Feel free to fork the project and contribute. To install diffpy.distanceprinter
in a development mode, with its sources being directly used by Python
rather than copied to a package directory, use the following in the root
directory ::

        pip install -e .

To ensure code quality and to prevent accidental commits into the default branch, please set up the use of our pre-commit
hooks.

1. Install pre-commit in your working environment by running ``conda install pre-commit``.

2. Initialize pre-commit (one time only) ``pre-commit install``.

Thereafter your code will be linted by black and isort and checked against flake8 before you can commit.
If it fails by black or isort, just rerun and it should pass (black and isort will modify the files so should
pass after they are modified). If the flake8 test fails please see the error messages and fix them manually before
trying to commit again.

Improvements and fixes are always appreciated.

Before contributing, please read our `Code of Conduct <https://github.com/diffpy/diffpy.distanceprinter/blob/main/CODE-OF-CONDUCT.rst>`_.

Getting Started
---------------

You may consult our `online documentation <https://diffpy.github.io/diffpy.distanceprinter>`_ for tutorials and API references.

Contact
-------

For more information on diffpy.distanceprinter please visit the project `web-page <https://www.diffpy.org>`_ or email Simon J.L. Billinge Group at sb2896@columbia.edu.

Acknowledgements
----------------

``diffpy.distanceprinter`` is built and maintained with `scikit-package <https://scikit-package.github.io/scikit-package/>`_.
