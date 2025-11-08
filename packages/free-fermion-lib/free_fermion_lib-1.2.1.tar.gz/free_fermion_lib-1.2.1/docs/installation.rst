Installation
============

Requirements
------------

The Free Fermion Library requires Python 3.8 or higher and the following dependencies:

* NumPy >= 1.20.0
* SciPy >= 1.7.0
* NetworkX >= 2.6.0
* Matplotlib >= 3.3.0

Install from PyPI
-----------------

The easiest way to install the Free Fermion Library is using pip::

    pip install free-fermion-lib

This will automatically install all required dependencies.

Install from Source
-------------------

To install the latest development version from GitHub::

    git clone https://github.com/jdwhitfield/free-fermion-lib.git
    cd free-fermion-lib
    pip install -e .

Development Installation
------------------------

For development work, install with optional development dependencies::

    git clone https://github.com/jdwhitfield/free-fermion-lib.git
    cd free-fermion-lib
    pip install -e ".[dev]"

This includes additional tools for testing and code quality:

* pytest >= 6.0
* pytest-cov >= 2.0
* black >= 21.0
* flake8 >= 3.8
* mypy >= 0.800

Documentation Dependencies
--------------------------

To build the documentation locally::

    pip install -e ".[docs]"

This includes:

* sphinx >= 4.0
* sphinx-rtd-theme >= 1.0
* nbsphinx >= 0.8

Virtual Environment Setup
-------------------------

It's recommended to use a virtual environment::

    # Create virtual environment
    python -m venv ff-env
    
    # Activate (Linux/macOS)
    source ff-env/bin/activate
    
    # Activate (Windows)
    ff-env\Scripts\activate
    
    # Install the library
    pip install free-fermion-lib

Conda Installation
------------------

If you prefer conda, you can create an environment with the required dependencies::

    conda create -n ff-env python=3.9 numpy scipy matplotlib networkx
    conda activate ff-env
    pip install free-fermion-lib

Verification
------------

To verify your installation, run::

    python -c "import ff; print(f'Free Fermion Library v{ff.__version__} installed successfully!')"

You should see output confirming the installation and version number.

Troubleshooting
---------------

Common Issues
~~~~~~~~~~~~~

**ImportError: No module named 'ff'**
    Make sure you've installed the package correctly. Try reinstalling with::
    
        pip uninstall free-fermion-lib
        pip install free-fermion-lib

**Dependency conflicts**
    If you encounter dependency conflicts, try creating a fresh virtual environment::
    
        python -m venv fresh-env
        source fresh-env/bin/activate  # or fresh-env\Scripts\activate on Windows
        pip install free-fermion-lib

**Jupyter notebook issues**
    If using Jupyter notebooks, make sure to install the library in the same environment as Jupyter::
    
        pip install jupyter
        pip install free-fermion-lib

Getting Help
~~~~~~~~~~~~

If you encounter issues:

1. Check the `GitHub Issues <https://github.com/jdwhitfield/free-fermion-lib/issues>`_
2. Create a new issue with details about your system and the error
3. Include the output of::

    python -c "import sys; print(sys.version)"
    pip list | grep -E "(numpy|scipy|networkx|matplotlib|free-fermion)"