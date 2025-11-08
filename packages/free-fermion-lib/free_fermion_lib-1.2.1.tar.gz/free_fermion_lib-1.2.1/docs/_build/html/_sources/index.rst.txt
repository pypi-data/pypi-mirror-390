Free Fermion Library Documentation
==================================

Welcome to the Free Fermion Library documentation! This library provides comprehensive tools for working with free fermion quantum systems, including combinatorial functions, graph theory algorithms, and quantum physics utilities.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   installation
   quickstart
   api
   tutorials
   examples
   contributing

Overview
--------

The Free Fermion Library is organized into four main modules:

* **ff_lib**: Core quantum physics and linear algebra functions
* **ff_combinatorics**: Combinatorial matrix functions (pfaffians, hafnians, etc.)
* **ff_graph_theory**: Graph algorithms and visualization for planar graphs
* **ff_utils**: Common utility functions

Key Features
------------

Core Quantum Physics Functions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* Jordan-Wigner transformations (Dirac and Majorana fermions)
* Symplectic free-fermion diagonalization
* Gaussian state generation and manipulation
* Fermionic correlation matrix computations
* Wick's theorem implementation

Combinatorial Functions
~~~~~~~~~~~~~~~~~~~~~~~

* Pfaffian computation via combinatorial formula
* Hafnian computation
* Permanent and determinant calculations
* Sign of permutation functions

Graph Theory Algorithms
~~~~~~~~~~~~~~~~~~~~~~~

* Pfaffian ordering algorithm (FKT algorithm) for planar graphs
* Perfect matching algorithms
* Planar graph generation and visualization
* Dual graph construction

Utility Functions
~~~~~~~~~~~~~~~~~

* Matrix cleaning and formatting
* Random bitstring generation
* Direct sum operations
* Pretty printing with numerical precision control

Quick Start
-----------

Installation::

    pip install free-fermion-lib

Basic usage::

    import numpy as np
    from ff import *

    # Generate Jordan-Wigner operators for 3 sites
    n_sites = 3
    alphas = jordan_wigner_alphas(n_sites)

    # Create a simple Hamiltonian matrix
    A = np.random.random((n_sites, n_sites))
    A = A + A.T  # Make symmetric
    H = build_H(n_sites, A)

    # Generate a Gaussian state
    rho = generate_gaussian_state(n_sites, H, alphas)

    # Compute correlation matrix
    gamma = compute_2corr_matrix(rho, n_sites, alphas)

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`