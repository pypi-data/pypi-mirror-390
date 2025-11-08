Tutorials
=========

This section contains detailed tutorials for using the Free Fermion Library.

.. note::
   These tutorials assume you have already installed the library and are familiar with the basic concepts from the :doc:`quickstart` guide.

Tutorial Topics
---------------

1. **Getting Started**
   
   * Basic library usage
   * Importing and setting up
   * Simple examples

2. **Jordan-Wigner Operators**
   
   * Creating fermionic operators
   * Majorana operators
   * Operator rotations and transformations

3. **Pfaffian Calculations**
   
   * Understanding pfaffians
   * Combinatorial calculations
   * Applications to quantum systems

4. **Graph Algorithms**
   
   * Planar graphs and embeddings
   * Perfect matching problems
   * Pfaffian ordering algorithm (FKT)

5. **Advanced Examples**
   
   * Symplectic diagonalization
   * Gaussian state manipulation
   * Complex quantum system analysis

Mathematical Background
-----------------------

Free Fermion Systems
~~~~~~~~~~~~~~~~~~~~

Free fermion systems are quantum many-body systems where particles don't interact directly. They can be described by quadratic Hamiltonians of the form:

.. math::

   H = \sum_{i,j} H_{ij} a_i^\dagger a_j + \frac{1}{2}\sum_{i,j} \Delta_{ij} a_i^\dagger a_j^\dagger + \text{h.c.}

where :math:`a_i^\dagger` and :math:`a_i` are fermionic creation and annihilation operators.

Jordan-Wigner Transformation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The Jordan-Wigner transformation maps fermionic operators to spin operators:

.. math::

   a_j = \left(\prod_{k<j} \sigma_k^z\right) \sigma_j^-

where :math:`\sigma_j^-` is the lowering operator at site :math:`j`.

Pfaffians and Perfect Matchings
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For a skew-symmetric matrix :math:`A`, the pfaffian is defined as:

.. math::

   \text{Pf}(A) = \frac{1}{2^{n/2} (n/2)!} \sum_{\sigma \in S_n} \text{sgn}(\sigma) \prod_{i=1}^{n/2} A_{\sigma(2i-1),\sigma(2i)}

The pfaffian counts perfect matchings in graphs, which is crucial for analyzing quantum systems.

Code Examples
-------------

Working with Correlation Matrices
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    import numpy as np
    import ff
    
    # Create a system with 4 sites
    n_sites = 4
    alphas = ff.jordan_wigner_alphas(n_sites)
    
    # Build a random Hamiltonian
    A = np.random.random((n_sites, n_sites))
    A = A + A.T  # Ensure Hermiticity
    H = ff.build_H(n_sites, A)
    
    # Generate the ground state
    rho = ff.generate_gaussian_state(n_sites, H, alphas)
    
    # Compute various correlation matrices
    gamma = ff.compute_2corr_matrix(rho, n_sites, alphas)
    cov = ff.compute_cov_matrix(rho, n_sites, alphas)
    
    print("Two-point correlations:")
    ff._print(gamma)
    
    print("\nCovariance matrix:")
    ff._print(cov)

Symplectic Eigenvalue Problems
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    # Diagonalize in symplectic form
    eigenvals, eigenvecs = ff.eigh_sp(H)
    
    # Verify symplectic property
    is_symplectic = ff.is_symp(eigenvecs)
    print(f"Eigenvectors are symplectic: {is_symplectic}")
    
    # Check canonical form
    is_canonical = ff.check_canonical_form(eigenvals)
    print(f"Eigenvalues in canonical form: {is_canonical}")

Graph Theory Applications
~~~~~~~~~~~~~~~~~~~~~~~~~

::

    # Generate a planar graph
    G = ff.generate_random_planar_graph(8, seed=123)
    
    if G is not None:
        # Apply pfaffian ordering
        pfo_matrix = ff.pfo_algorithm(G, verbose=True)
        
        # Find perfect matchings
        matchings = ff.find_perfect_matchings(G)
        
        # Compute pfaffian (should equal number of matchings)
        pf_value = ff.pf(pfo_matrix)
        
        print(f"Number of perfect matchings: {len(matchings)}")
        print(f"Pfaffian value: {pf_value}")

Best Practices
--------------

Performance Tips
~~~~~~~~~~~~~~~~

1. **Use appropriate data types**: Complex matrices when necessary, real when possible
2. **Leverage NumPy broadcasting**: Avoid explicit loops when possible
3. **Clean numerical noise**: Use ``ff.clean()`` to remove small numerical artifacts
4. **Check matrix properties**: Verify Hermiticity, skew-symmetry as appropriate

Numerical Stability
~~~~~~~~~~~~~~~~~~~

1. **Monitor condition numbers**: Large condition numbers indicate numerical instability
2. **Use appropriate tolerances**: Adjust thresholds in ``ff.clean()`` based on your precision needs
3. **Validate results**: Check physical properties like trace preservation, unitarity

Common Pitfalls
~~~~~~~~~~~~~~~

1. **Operator ordering**: Remember that fermionic operators anticommute
2. **Matrix dimensions**: Ensure compatibility between operators and coefficient matrices
3. **Normalization**: Check that states are properly normalized
4. **Boundary conditions**: Be aware of how boundary conditions affect results

Further Reading
---------------

* Lieb, E. H., Schultz, T., & Mattis, D. (1961). Two soluble models of an antiferromagnetic chain.
* Kitaev, A. (2001). Unpaired Majorana fermions in quantum wires.
* Bravyi, S. (2005). Lagrangian representation for fermionic linear optics.
* Kraus, C. V., et al. (2013). Fermionic quantum computation.