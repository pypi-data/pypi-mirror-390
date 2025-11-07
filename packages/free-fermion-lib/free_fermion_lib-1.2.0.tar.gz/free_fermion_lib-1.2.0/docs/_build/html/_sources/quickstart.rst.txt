Quick Start Guide
=================

This guide will get you up and running with the Free Fermion Library in just a few minutes.

Basic Import
------------

After installation, import the library::

    import numpy as np
    import ff

All functions are available directly from the ``ff`` namespace.

Jordan-Wigner Operators
-----------------------

Generate fermionic operators using the Jordan-Wigner transformation::

    # Create operators for 3 sites
    n_sites = 3
    alphas = ff.jordan_wigner_alphas(n_sites)
    
    print(f"Generated {len(alphas)} operators")
    print(f"Each operator has shape: {alphas[0].shape}")

This creates both raising and lowering operators: ``[a†₀, a†₁, a†₂, a₀, a₁, a₂]``

Majorana Operators
~~~~~~~~~~~~~~~~~~

You can also generate Majorana operators::

    majoranas = ff.jordan_wigner_majoranas(n_sites)
    print(f"Generated {len(majoranas)} Majorana operators")

Combinatorial Functions
-----------------------

Pfaffian Calculation
~~~~~~~~~~~~~~~~~~~~

Compute the pfaffian of a skew-symmetric matrix::

    # Create a skew-symmetric matrix
    A = np.array([[0, 1, -2], 
                  [-1, 0, 3], 
                  [2, -3, 0]])
    
    pfaffian_value = ff.pf(A)
    print(f"Pfaffian: {pfaffian_value}")

Other Combinatorial Functions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    # Determinant
    B = np.random.random((3, 3))
    det_val = ff.dt(B)
    
    # Permanent
    perm_val = ff.pt(B)
    
    # Hafnian (for even-dimensional matrices)
    C = np.random.random((4, 4))
    haf_val = ff.hf(C)

Hamiltonian Construction
------------------------

Build coefficient matrices for quadratic Hamiltonians::

    # Create a random symmetric matrix
    A = np.random.random((n_sites, n_sites))
    A = A + A.T  # Make symmetric
    
    # Build H-form coefficient matrix
    H = ff.build_H(n_sites, A)
    print(f"H matrix shape: {H.shape}")
    
    # Build V-form coefficient matrix  
    V = ff.build_V(n_sites, A)
    print(f"V matrix shape: {V.shape}")

Gaussian States
---------------

Generate random Gaussian states ::

    # Generate a Gaussian state
    rho = ff.random_FF_state(n_sites)
    print(f"Generated state shape: {rho.shape}")
    
    # Verify it's normalized
    trace = np.trace(rho)
    print(f"Trace (should be 1): {trace}")
    
Generate Gaussian state from random quadratic Hamiltonian:: 
    # Generate random quadratic Hamiltonian
    A = np.random.randn((n_sites, n_sites))+1j*np.random.randn((n_sites, n_sites))
    Z = np.random.randn((n_sites, n_sites))+1j*np.random.randn((n_sites, n_sites))
    A = A + A.conj().T  # Ensure Hermiticity
    Z = Z - Z.T # Ensure skew-symmetry
    
    # build [(2 n_sites) x (2 n_sites) ]  coefficient matrix
    H = ff.build_H(n_sites,A,Z)

    #build n-body operator \hat H [2**n_sites x 2**n_sites]
    H_op = ff.build_op(H, n_sites, alphas)

    # FF state
    rho = scipy.linalg.expm(-H_op)  # Exponential of the parent Hamiltonian
    rho /= np.trace(rho)  # Normalize the state

    print(f"Generated state with Hamiltonian shape: {rho.shape}")
    print(f"State matrix shape: {rho.shape}")
    
    # Verify it's normalized
    trace = np.trace(rho)
    print(f"Trace (should be 1): {trace}")

Correlation Matrices
--------------------

Compute fermionic correlation matrices::

    # Two-point correlation matrix
    gamma = ff.compute_2corr_matrix(rho, n_sites, alphas)
    print(f"Correlation matrix shape: {gamma.shape}")
    
    # Covariance matrix
    cov = ff.compute_cov_matrix(rho, n_sites, alphas)
    print(f"Covariance matrix shape: {cov.shape}")

Symplectic Diagonalization
---------------------------

Diagonalize coefficient matrices in symplectic form::

    # Symplectic eigendecomposition
    eigenvals, eigenvecs = ff.eigh_sp(H)
    
    print(f"Eigenvalues shape: {eigenvals.shape}")
    print(f"Eigenvectors shape: {eigenvecs.shape}")
    
    # Check if eigenvectors are symplectic
    is_symplectic = ff.is_symp(eigenvecs)
    print(f"Eigenvectors are symplectic: {is_symplectic}")

Graph Theory
------------

Work with planar graphs and perfect matchings::

    # Generate a random planar graph
    G = ff.generate_random_planar_graph(6, seed=42)
    
    if G is not None:
        # Find perfect matchings
        matchings = ff.find_perfect_matchings(G)
        print(f"Found {len(matchings)} perfect matchings")
        
        # Apply pfaffian ordering algorithm
        pfo_matrix = ff.pfo_algorithm(G, verbose=False)
        print(f"PFO matrix shape: {pfo_matrix.shape}")

Utility Functions
-----------------

Clean numerical arrays::

    # Create array with small numerical noise
    noisy_array = np.array([1.0, 1e-10, 2.0, 1e-15, 3.0])
    
    # Clean small values
    cleaned = ff.clean(noisy_array, threshold=1e-8)
    print(f"Original: {noisy_array}")
    print(f"Cleaned:  {cleaned}")

Pretty printing with controlled precision::

    # Print with specific precision
    matrix = np.random.random((3, 3)) + 1e-10 * np.random.random((3, 3))
    ff._print(matrix, k=4)  # Print with 4 decimal places

Complete Example
----------------

Here's a complete example that demonstrates the main workflow::

    import numpy as np
    import ff
    
    # Setup
    n_sites = 2
    alphas = ff.jordan_wigner_alphas(n_sites)
    
    seed = 42

    # Generate random Gaussian state
    rho, H = ff.random_FF_state(n_sites, returnH=True)
    
    # Compute correlation matrix
    gamma = ff.compute_2corr_matrix(rho, n_sites, alphas)
    
    # Diagonalize
    eigenvals, eigenvecs = ff.eigh_sp(H)
    
    # Print results
    print("Parent Hamiltonian eigenvalues:")
    ff._print(np.diag(eigenvals))
    
    print("\nCorrelation matrix:")
    ff._print(gamma)

This example shows the typical workflow: create operators, build Hamiltonians, generate states, and analyze their properties.

Next Steps
----------

* Explore the :doc:`api` for detailed function documentation
* Check out :doc:`tutorials` for more advanced examples
* Look at :doc:`examples` for specific use cases