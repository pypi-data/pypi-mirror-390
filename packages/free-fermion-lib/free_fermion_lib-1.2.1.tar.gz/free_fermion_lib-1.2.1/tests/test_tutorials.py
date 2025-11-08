"""
Tutorial Validation Tests for Free Fermion Library

This module contains tests that validate all the code examples from docs/tutorials.rst
to ensure that the documented tutorial examples work correctly.

Test categories:
- Working with Correlation Matrices (tutorials.rst lines 95-123)
- Symplectic Eigenvalue Problems (tutorials.rst lines 125-139)
- Graph Theory Applications (tutorials.rst lines 141-160)
"""

import networkx as nx
import numpy as np
import pytest

# Import the library
import ff


class TestCorrelationMatricesTutorial:
    """Test the correlation matrices tutorial example from tutorials.rst lines 95-123"""

    @pytest.mark.tutorial
    def test_correlation_matrices_tutorial(self, random_seed):
        """Test the correlation matrices example from tutorials.rst lines 95-123"""
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

        # Validate results
        assert gamma.shape == (2 * n_sites, 2 * n_sites), "Gamma should be 2N x 2N"
        assert cov.shape == (2 * n_sites, 2 * n_sites), "Covariance should be 2N x 2N"

        # Check that the state is normalized
        assert np.allclose(np.trace(rho), 1.0), "State should be normalized"

        # Check that rho is positive semidefinite (eigenvalues >= 0)
        eigenvals = np.linalg.eigvals(rho)
        assert np.all(eigenvals >= -1e-10), "State should be positive semidefinite"

        # Check that gamma has the right structure for correlation matrix
        # For a properly normalized state, diagonal elements should be real
        gamma_diag = np.diag(gamma)
        assert np.allclose(gamma_diag.imag, 0), "Diagonal of gamma should be real"

    @pytest.mark.tutorial
    def test_correlation_matrices_properties(self, small_system):
        """Test mathematical properties of correlation matrices"""
        system = small_system
        n_sites = system["n_sites"]
        H = system["H"]
        alphas = system["alphas"]

        # Generate the ground state
        rho = ff.generate_gaussian_state(n_sites, H, alphas)

        # Compute correlation matrices
        gamma = ff.compute_2corr_matrix(rho, n_sites, alphas)
        cov = ff.compute_cov_matrix(rho, n_sites, alphas)

        # Test covariance matrix properties
        # Covariance should be antisymmetric: K_ij = -K_ji
        assert np.allclose(cov, -cov.T), "Covariance matrix should be antisymmetric"

        # Test that correlation matrix has proper trace properties
        # The trace should be related to particle number
        trace_gamma = np.trace(gamma)
        assert np.isfinite(trace_gamma), "Trace of gamma should be finite"


class TestSymplecticEigenvalueTutorial:
    """Test symplectic eigenvalue example from tutorials.rst lines 125-139"""

    @pytest.mark.tutorial
    def test_symplectic_eigenvalue_tutorial(self, random_seed):
        """Test symplectic eigenvalue example from tutorials.rst lines 125-139"""
        n_sites = 4
        A = np.random.random((n_sites, n_sites))
        A = A + A.T  # Ensure Hermiticity
        H = ff.build_H(n_sites, A)

        # Diagonalize in symplectic form
        eigenvals, eigenvecs = ff.eigh_sp(H)

        # Verify symplectic property
        is_symplectic = ff.is_symp(eigenvecs)
        assert is_symplectic, "Eigenvectors should be symplectic"

        # Check that eigenvalues appear as np.block([Sigma, 0], [0,-Sigma])
        assert np.allclose(
            np.diag(eigenvals)[n_sites:], -np.diag(eigenvals)[:n_sites]
        ), "Eigenvalues should appear in +/- pairs"

        # Verify that the diagonalization is correct: U† H U = L
        H_diag = eigenvecs.conj().T @ H @ eigenvecs
        assert np.allclose(H_diag, eigenvals), "Diagonalization should be correct"

    @pytest.mark.tutorial
    def test_symplectic_properties(self, medium_system):
        """Test detailed symplectic properties"""
        system = medium_system
        H = system["H"]
        n_sites = H.shape[0] // 2

        # Diagonalize
        eigenvals, eigenvecs = ff.eigh_sp(H)

        # Test that eigenvectors form a symplectic matrix
        assert ff.is_symp(eigenvecs), "Eigenvectors should be symplectic"

        # Check that eigenvalues appear as np.block([Sigma, 0], [0,-Sigma])
        assert np.allclose(
            np.diag(eigenvals)[n_sites:], -np.diag(eigenvals)[:n_sites]
        ), "Eigenvalues should appear in +/- pairs"

        # Test that the transformation preserves the symplectic structure
        # For symplectic matrices: U S U^T = S where S is the symplectic form
        S = np.zeros_like(H)
        S[:n_sites, n_sites:] = np.eye(n_sites)
        S[n_sites:, :n_sites] = np.eye(n_sites)

        S_transformed = eigenvecs @ S @ eigenvecs.T
        assert np.allclose(S_transformed, S), "Symplectic form should be preserved"


class TestGraphTheoryTutorial:
    """Test graph theory example from tutorials.rst lines 141-160"""

    @pytest.mark.tutorial
    def test_graph_theory_tutorial(self, random_seed):
        """Test graph theory example from tutorials.rst lines 141-160"""
        # Generate a planar graph
        G = ff.generate_random_planar_graph(8, seed=123)

        if G is not None:
            # Verify the graph is planar
            is_planar, _ = nx.check_planarity(G)
            assert is_planar, "Generated graph should be planar"

            # # Compute and apply the pfaffian ordering
            # A = nx.adjacency_matrix(G).toarray()
            # pfo = ff.pfo_algorithm(G, verbose=False)
            # pfoA = np.multiply(pfo,A)
            # pfoA = np.triu(pfoA)
            # pfoA = pfoA - pfoA.T
            # pfoA = np.multiply(pfo,A)

            # # Find perfect matchings
            # matchings = ff.find_perfect_matchings_brute(G)

            # # Compute pfaffian (should equal number of matchings)
            # pf_value = ff.pf(pfoA)

            # Get adjacency matrix
            A = nx.adjacency_matrix(G).toarray()

            # Compute and apply the pfaffian ordering
            pfo = ff.pfo_algorithm(G)
            pfoA = np.multiply(pfo, A)

            # Ensure pfoA is skew-symmetric
            pfoA = np.triu(pfoA)
            pfoA = pfoA - pfoA.T

            # compute the pfaffian
            pf_value = ff.pf(pfoA)

            # Find perfect matchings
            matchings = ff.find_perfect_matchings_brute(G)
            nmatchings = len(matchings)

            # Validate results
            assert nmatchings == int(
                abs(pf_value)
            ), "Pfaffian should equal number of perfect matchings"
            assert pfoA.shape[0] == len(G.nodes()), "PFO matrix should match graph size"

            # Verify PFO matrix is skew-symmetric
            assert np.allclose(pfoA, -pfoA.T), "PFO matrix should be skew-symmetric"

    @pytest.mark.tutorial
    def test_small_graph_perfect_matching(self):
        """Test perfect matching on a simple known graph"""
        # Create a simple 4-cycle (square)
        G = nx.cycle_graph(4)

        PMs = ff.find_perfect_matchings_brute(G)
        # Should have 2 perfect matchings: (0,1)(2,3) and (0,3)(1,2)
        assert len(PMs) == 2, "4-cycle should have 2 perfect matchings"

        # Find perfect matchings
        nmatchings = ff.clean(ff.count_perfect_matchings(G))

        # A 4-cycle should have exactly 2 perfect matchings
        assert nmatchings == 2, "4-cycle should have 2 perfect matchings"

        # Get adjacency matrix
        A = nx.adjacency_matrix(G).toarray()

        # Compute and apply the pfaffian ordering
        pfo = ff.pfo_algorithm(G)
        pfoA = np.multiply(pfo, A)

        # Ensure pfoA is skew-symmetric
        pfoA = np.triu(pfoA)
        pfoA = pfoA - pfoA.T

        # compute the pfaffian
        pf_value = ff.pf(pfoA)

        # Verify pfaffian equals number of matchings
        assert (
            abs(pf_value) == nmatchings
        ), "Pfaffian should equal number of perfect matchings"

    @pytest.mark.tutorial
    def test_graph_with_no_perfect_matching(self):
        """Test behavior with graphs that have no perfect matchings"""
        # Create a triangle (odd number of vertices)
        G = nx.cycle_graph(3)

        # Should have no perfect matchings
        matchings = ff.find_perfect_matchings_brute(G)
        assert len(matchings) == 0, "Triangle should have no perfect matchings"

        # PFO algorithm should still work but give pfaffian = 0

        # Compute and apply the pfaffian ordering
        A = nx.adjacency_matrix(G).toarray()

        pfo = ff.pfo_algorithm(G, verbose=False)
        pfoA = np.multiply(pfo, A)
        pfoA = np.triu(pfoA)
        pfoA = pfoA - pfoA.T
        pfoA = np.multiply(pfo, A)

        pf_value = ff.pf(pfoA)

        # For odd graphs, pfaffian should be 0
        assert abs(pf_value) < 1e-10, "Pfaffian of odd graph should be 0"


class TestTutorialMathematicalBackground:
    """Test examples from the mathematical background section"""

    @pytest.mark.tutorial
    def test_jordan_wigner_transformation(self):
        """Test basic Jordan-Wigner transformation properties"""
        n_sites = 3

        # Get fermionic operators
        alphas = ff.jordan_wigner_alphas(n_sites)

        # Test that we have the right number of operators
        assert len(alphas) == 2 * n_sites, "Should have 2N operators"

        # Test that operators have the right dimensions
        expected_dim = 2**n_sites
        for alpha in alphas:
            assert alpha.shape == (
                expected_dim,
                expected_dim,
            ), f"Operators should be {expected_dim}x{expected_dim}"

    @pytest.mark.tutorial
    def test_majorana_operators(self):
        """Test Majorana operator properties"""
        n_sites = 2
        majoranas = ff.jordan_wigner_majoranas(n_sites)

        # Should have 2N Majorana operators
        assert len(majoranas) == 2 * n_sites, "Should have 2N Majorana operators"

        # Test Hermiticity: γ† = γ
        for gamma in majoranas:
            assert np.allclose(
                gamma, gamma.conj().T
            ), "Majorana operators should be Hermitian"

    @pytest.mark.tutorial
    def test_free_fermion_hamiltonian_structure(self):
        """Test the structure of free fermion Hamiltonians"""
        n_sites = 3

        # Create a random Hermitian hopping matrix
        A = np.random.randn(n_sites, n_sites)
        A = A + A.T

        # Create a random antisymmetric pairing matrix
        B = np.random.randn(n_sites, n_sites)
        B = B - B.T

        # Build the Hamiltonian
        H = ff.build_H(n_sites, A, B)

        # Test the block structure
        assert H.shape == (2 * n_sites, 2 * n_sites), "H should be 2N x 2N"

        # Check block structure: H = [[-A*, B], [-B*, A]]
        assert np.allclose(
            H[:n_sites, :n_sites], -A.conj()
        ), "Top-left block should be -A*"
        assert np.allclose(H[:n_sites, n_sites:], B), "Top-right block should be B"
        assert np.allclose(
            H[n_sites:, :n_sites], -B.conj()
        ), "Bottom-left block should be -B*"
        assert np.allclose(H[n_sites:, n_sites:], A), "Bottom-right block should be A"


class TestTutorialBestPractices:
    """Test the best practices examples from tutorials"""

    @pytest.mark.tutorial
    def test_numerical_cleaning(self):
        """Test numerical cleaning best practices"""
        # Create a matrix with numerical noise
        clean_matrix = np.array([[1.0, 0.0, 0.5], [0.0, 2.0, 0.0], [0.5, 0.0, 1.5]])

        noise = 1e-12 * np.random.randn(3, 3)
        noisy_matrix = clean_matrix + noise

        # Clean the matrix
        cleaned = ff.clean(noisy_matrix, threshold=1e-10)

        # Should be close to the original clean matrix
        assert np.allclose(
            cleaned, clean_matrix, atol=1e-10
        ), "Cleaned matrix should match original"

    @pytest.mark.tutorial
    def test_matrix_property_checking(self):
        """Test checking matrix properties as recommended"""
        n_sites = 2

        # Create a Hermitian matrix
        A = np.array([[1.0, 0.5], [0.5, 1.0]])
        assert np.allclose(A, A.conj().T), "A should be Hermitian"

        # Create a skew-symmetric matrix
        B = np.array([[0, 0.2], [-0.2, 0]])
        assert np.allclose(B, -B.T), "B should be skew-symmetric"

        # Build Hamiltonian and check its properties
        H = ff.build_H(n_sites, A, B)

        # The Hamiltonian should have the right structure for symplectic diagonalization
        eigenvals, eigenvecs = ff.eigh_sp(H)
        assert ff.is_symp(eigenvecs), "Eigenvectors should be symplectic"
        # Check that eigenvalues appear as np.block([Sigma, 0], [0,-Sigma])
        assert np.allclose(
            np.diag(eigenvals)[n_sites:], -np.diag(eigenvals)[:n_sites]
        ), "Eigenvalues should appear in +/- pairs"

    @pytest.mark.tutorial
    def test_state_normalization_checking(self):
        """Test checking state normalization as recommended"""
        n_sites = 2
        A = np.array([[1.0, 0.5], [0.5, 1.0]])
        H = ff.build_H(n_sites, A)
        alphas = ff.jordan_wigner_alphas(n_sites)

        # Generate state
        rho = ff.generate_gaussian_state(n_sites, H, alphas)

        # Check normalization
        trace_rho = np.trace(rho)
        assert np.allclose(trace_rho, 1.0), "State should be normalized"

        # Check positive semidefiniteness
        eigenvals = np.linalg.eigvals(rho)
        assert np.all(eigenvals >= -1e-10), "State should be positive semidefinite"
