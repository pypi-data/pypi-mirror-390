Examples
========

This page contains practical examples demonstrating various use cases of the Free Fermion Library.

Basic Examples
--------------

Simple Pfaffian Calculation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    import numpy as np
    import ff
    
    # Create a 4x4 skew-symmetric matrix
    A = np.array([[0, 1, 2, 3],
                  [-1, 0, 4, 5],
                  [-2, -4, 0, 6],
                  [-3, -5, -6, 0]])
    
    # Compute pfaffian
    pf_value = ff.pf(A)
    print(f"Pfaffian: {pf_value}")
    
    # Verify: pf(A)^2 should equal det(A)
    det_value = np.linalg.det(A)
    print(f"det(A): {det_value}")
    print(f"pf(A)^2: {pf_value**2}")

Two-Site System Analysis
~~~~~~~~~~~~~~~~~~~~~~~~

::

    import numpy as np
    import ff
    
    # Two-site system
    n_sites = 2
    alphas = ff.jordan_wigner_alphas(n_sites)
    
    # Hopping Hamiltonian: H = -t(a†₀a₁ + a†₁a₀)
    t = 1.0
    A = np.array([[0, -t], [-t, 0]])
    H = ff.build_H(n_sites, A)
    
    print("Hamiltonian coefficient matrix:")
    ff._print(H)
    
    # Generate ground state
    rho = ff.generate_gaussian_state(n_sites, H, alphas)
    
    # Compute correlation matrix
    gamma = ff.compute_2corr_matrix(rho, n_sites, alphas)
    
    print("\nCorrelation matrix:")
    ff._print(gamma)

Intermediate Examples
---------------------

Kitaev Chain Model
~~~~~~~~~~~~~~~~~~

::

    import numpy as np
    import ff
    
    def kitaev_chain(n_sites, mu, t, delta):
        """
        Create Kitaev chain Hamiltonian.
        H = -μΣᵢnᵢ - tΣᵢ(a†ᵢaᵢ₊₁ + h.c.) + ΔΣᵢ(aᵢaᵢ₊₁ + h.c.)
        """
        # Chemical potential term
        A = -mu * np.eye(n_sites)
        
        # Hopping term
        for i in range(n_sites - 1):
            A[i, i+1] = -t
            A[i+1, i] = -t
        
        # Pairing term
        B = np.zeros((n_sites, n_sites))
        for i in range(n_sites - 1):
            B[i, i+1] = delta
            B[i+1, i] = -delta
        
        return ff.build_H(n_sites, A, B)
    
    # Parameters
    n_sites = 6
    mu = 0.5      # Chemical potential
    t = 1.0       # Hopping strength
    delta = 0.8   # Pairing strength
    
    # Build Hamiltonian
    H = kitaev_chain(n_sites, mu, t, delta)
    
    # Diagonalize
    eigenvals, eigenvecs = ff.eigh_sp(H)
    
    print("Energy eigenvalues:")
    energies = np.diag(eigenvals)[n_sites:]  # Positive eigenvalues
    ff._print(energies)
    
    # Check for zero modes (topological phase)
    zero_modes = np.abs(energies) < 1e-10
    print(f"\nNumber of zero modes: {np.sum(zero_modes)}")

Random Matrix Ensemble
~~~~~~~~~~~~~~~~~~~~~~

::

    import numpy as np
    import ff
    import matplotlib.pyplot as plt
    
    def random_gaussian_ensemble(n_sites, num_samples=100):
        """Generate statistics for random Gaussian ensembles."""
        eigenvalues = []
        
        for _ in range(num_samples):
            # Random Hermitian matrix
            A = np.random.randn(n_sites, n_sites)
            A = A + A.T
            
            # Build Hamiltonian
            H = ff.build_H(n_sites, A)
            
            # Diagonalize
            evals, _ = ff.eigh_sp(H)
            eigenvalues.extend(np.diag(evals)[n_sites:])
        
        return np.array(eigenvalues)
    
    # Generate ensemble
    n_sites = 4
    eigenvals = random_gaussian_ensemble(n_sites, num_samples=200)
    
    print(f"Generated {len(eigenvals)} eigenvalues")
    print(f"Mean: {np.mean(eigenvals):.3f}")
    print(f"Std:  {np.std(eigenvals):.3f}")

Advanced Examples
-----------------

Correlation Function Analysis
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    import numpy as np
    import ff
    
    def analyze_correlations(n_sites, A_matrix):
        """Analyze correlation functions for a given system."""
        alphas = ff.jordan_wigner_alphas(n_sites)
        H = ff.build_H(n_sites, A_matrix)
        rho = ff.generate_gaussian_state(n_sites, H, alphas)
        
        # Compute different correlation matrices
        gamma = ff.compute_2corr_matrix(rho, n_sites, alphas)
        cov = ff.compute_cov_matrix(rho, n_sites, alphas)
        
        # Extract physical quantities
        occupations = np.diag(gamma)[n_sites:]  # ⟨a†ᵢaᵢ⟩
        
        # Correlation lengths (simplified)
        correlations = []
        for i in range(n_sites):
            for j in range(i+1, n_sites):
                corr = gamma[i, j + n_sites]  # ⟨a†ᵢaⱼ⟩
                correlations.append((j-i, abs(corr)))
        
        return {
            'occupations': occupations,
            'correlations': correlations,
            'gamma': gamma,
            'covariance': cov
        }
    
    # Example: Uniform hopping chain
    n_sites = 6
    A = np.zeros((n_sites, n_sites))
    for i in range(n_sites - 1):
        A[i, i+1] = A[i+1, i] = -1.0
    
    results = analyze_correlations(n_sites, A)
    
    print("Site occupations:")
    ff._print(results['occupations'])
    
    print("\nDistance vs correlation strength:")
    for dist, corr in results['correlations'][:5]:
        print(f"Distance {dist}: {corr:.4f}")

Perfect Matching in Graphs
~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    import numpy as np
    import ff
    import networkx as nx
    
    def analyze_perfect_matchings(n_vertices):
        """Analyze perfect matchings using pfaffian method."""
        if n_vertices % 2 != 0:
            print("Need even number of vertices for perfect matchings")
            return
        
        # Generate random planar graph
        G = ff.generate_random_planar_graph(n_vertices, seed=42)
        
        if G is None:
            print("Could not generate planar graph")
            return
        
        # Method 1: Brute force enumeration
        matchings_brute = ff.find_perfect_matchings(G)
        
        # Method 2: Pfaffian calculation
        pfo_matrix = ff.pfo_algorithm(G, verbose=False)
        pf_value = ff.pf(pfo_matrix)
        
        print(f"Graph with {n_vertices} vertices:")
        print(f"Edges: {G.number_of_edges()}")
        print(f"Perfect matchings (brute force): {len(matchings_brute)}")
        print(f"Perfect matchings (pfaffian): {int(abs(pf_value))}")
        
        # Verify they match
        if abs(len(matchings_brute) - abs(pf_value)) < 1e-10:
            print("✓ Methods agree!")
        else:
            print("✗ Methods disagree!")
        
        return G, matchings_brute, pfo_matrix
    
    # Test with different sizes
    for n in [4, 6, 8]:
        print(f"\n{'-'*40}")
        analyze_perfect_matchings(n)

Symplectic Geometry Example
~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    import numpy as np
    import ff
    
    def symplectic_transformation_example():
        """Demonstrate symplectic transformations."""
        n_sites = 3
        
        # Create random Hamiltonian
        A = np.random.randn(n_sites, n_sites)
        A = A + A.T
        H = ff.build_H(n_sites, A)
        
        print("Original Hamiltonian:")
        ff._print(H)
        
        # Symplectic diagonalization
        L, U = ff.eigh_sp(H)
        
        print(f"\nSymplectic matrix U is symplectic: {ff.is_symp(U)}")
        print(f"Eigenvalue matrix in canonical form: {ff.check_canonical_form(L)}")
        
        # Verify diagonalization: U† H U = L
        H_diag = U.conj().T @ H @ U
        
        print("\nDiagonalized Hamiltonian:")
        ff._print(H_diag)
        
        print("\nExpected eigenvalue structure:")
        ff._print(L)
        
        # Check if they match
        if np.allclose(H_diag, L):
            print("✓ Diagonalization successful!")
        else:
            print("✗ Diagonalization failed!")
        
        return H, L, U
    
    symplectic_transformation_example()

Utility Examples
----------------

Matrix Cleaning
~~~~~~~~~~~~~~~

::

    import numpy as np
    import ff
    
    # Create matrix with numerical noise
    clean_matrix = np.array([[1.0, 0.0, 0.5],
                            [0.0, 2.0, 0.0],
                            [0.5, 0.0, 1.5]])
    
    noise = 1e-12 * np.random.randn(3, 3)
    noisy_matrix = clean_matrix + noise
    
    print("Original clean matrix:")
    ff._print(clean_matrix)
    
    print("\nWith numerical noise:")
    ff._print(noisy_matrix, k=15)
    
    print("\nAfter cleaning:")
    cleaned = ff.clean(noisy_matrix, threshold=1e-10)
    ff._print(cleaned)

Custom Printing
~~~~~~~~~~~~~~~

::

    import numpy as np
    import ff
    
    # Complex matrix with varying magnitudes
    matrix = np.array([[1.23456789, 1e-8 + 2.3456j],
                      [0.000123456, 9.87654321]])
    
    print("Default NumPy printing:")
    print(matrix)
    
    print("\nCustom precision (3 decimal places):")
    ff._print(matrix, k=3)
    
    print("\nCustom precision (6 decimal places):")
    ff._print(matrix, k=6)

Performance Examples
--------------------

Large System Benchmark
~~~~~~~~~~~~~~~~~~~~~~

::

    import numpy as np
    import ff
    import time
    
    def benchmark_large_system(n_sites):
        """Benchmark performance for large systems."""
        print(f"Benchmarking {n_sites}-site system...")
        
        # Generate random Hamiltonian
        A = np.random.randn(n_sites, n_sites)
        A = A + A.T
        
        # Time Hamiltonian construction
        start = time.time()
        H = ff.build_H(n_sites, A)
        h_time = time.time() - start
        
        # Time diagonalization
        start = time.time()
        eigenvals, eigenvecs = ff.eigh_sp(H)
        diag_time = time.time() - start
        
        # Time state generation
        alphas = ff.jordan_wigner_alphas(n_sites)
        start = time.time()
        rho = ff.generate_gaussian_state(n_sites, H, alphas)
        state_time = time.time() - start
        
        print(f"  Hamiltonian construction: {h_time:.4f}s")
        print(f"  Diagonalization: {diag_time:.4f}s")
        print(f"  State generation: {state_time:.4f}s")
        print(f"  Total: {h_time + diag_time + state_time:.4f}s")
    
    # Benchmark different sizes
    for n in [5, 10, 15]:
        benchmark_large_system(n)
        print()