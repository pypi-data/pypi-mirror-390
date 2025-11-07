"""
Example Validation Tests for Free Fermion Library

This module contains tests that validate all the code examples from docs/examples.rst
to ensure that the documented examples work correctly.

Test categories:
- Basic Examples (Simple pfaffian, two-site system)
- Intermediate Examples (Kitaev chain, random matrix ensemble)
- Advanced Examples (Correlation analysis, perfect matching, symplectic transformations)
- Utility Examples (Matrix cleaning, custom printing)
- Performance Examples (Large system benchmarks)
"""

import time

import networkx as nx
import numpy as np
import pytest

# Import the library
import ff


class TestBasicExamples:
    """Test basic examples from docs/examples.rst"""

    @pytest.mark.example
    def test_simple_pfaffian_example(self):
        """Test simple pfaffian example from examples.rst lines 9-30"""
        # Create a 4x4 skew-symmetric matrix
        A = np.array([[0, 1, 2, 3], [-1, 0, 4, 5], [-2, -4, 0, 6], [-3, -5, -6, 0]])

        # Compute pfaffian
        pf_value = ff.pf(A)

        # Verify: pf(A)^2 should equal det(A)
        det_value = np.linalg.det(A)

        assert np.allclose(pf_value**2, det_value), "pf(A)^2 should equal det(A)"
        assert np.allclose(A, -A.T), "Matrix should be skew-symmetric"

        # Additional validation: pfaffian should be real for real skew-symmetric matrix
        assert np.allclose(pf_value.imag, 0), "Pfaffian should be real for real matrix"

    @pytest.mark.example
    def test_two_site_system_example(self):
        """Test two-site system from examples.rst lines 32-59"""
        # Two-site system
        n_sites = 2
        alphas = ff.jordan_wigner_alphas(n_sites)

        # Hopping Hamiltonian: H = -t(a†₀a₁ + a†₁a₀)
        t = 1.0
        A = np.array([[0, -t], [-t, 0]])
        H = ff.build_H(n_sites, A)

        # Generate ground state
        rho = ff.generate_gaussian_state(n_sites, H, alphas)

        # Compute correlation matrix
        gamma = ff.compute_2corr_matrix(rho, n_sites, alphas)

        # Validate results
        assert H.shape == (4, 4), "H should be 4x4 for 2-site system"
        assert gamma.shape == (4, 4), "Gamma should be 4x4"
        assert np.allclose(np.trace(rho), 1.0), "State should be normalized"

        # Check that the Hamiltonian has the expected structure
        expected_H = np.array(
            [[0, t, 0, 0], [t, 0, 0, 0], [0, 0, 0, -t], [0, 0, -t, 0]]
        )
        assert np.allclose(H, expected_H), "H should match expected structure"


class TestIntermediateExamples:
    """Test intermediate examples from docs/examples.rst"""

    @pytest.mark.example
    def test_kitaev_chain_example(self):
        """Test Kitaev chain model from examples.rst lines 64-111"""

        def kitaev_chain(n_sites, mu, t, delta):
            """Create Kitaev chain Hamiltonian."""
            # Chemical potential term
            A = -mu * np.eye(n_sites)

            # Hopping term
            for i in range(n_sites - 1):
                A[i, i + 1] = -t
                A[i + 1, i] = -t

            # Pairing term
            B = np.zeros((n_sites, n_sites))
            for i in range(n_sites - 1):
                B[i, i + 1] = delta
                B[i + 1, i] = -delta

            return ff.build_H(n_sites, A, B)

        # Parameters
        n_sites = 6
        mu = 0.5  # Chemical potential
        t = 1.0  # Hopping strength
        delta = 0.8  # Pairing strength

        # Build Hamiltonian
        H = kitaev_chain(n_sites, mu, t, delta)

        # Diagonalize
        eigenvals, eigenvecs = ff.eigh_sp(H)

        # Validate results
        assert H.shape == (2 * n_sites, 2 * n_sites), "H should be 2N x 2N"
        assert ff.is_symp(eigenvecs), "Eigenvectors should be symplectic"
        assert np.allclose(
            np.diag(eigenvals)[n_sites:], -np.diag(eigenvals)[:n_sites]
        ), "Eigenvalues should appear in +/- pairs"

        # Check for energy spectrum properties
        pos_energies = np.diag(eigenvals)[
            np.diag(eigenvals) >= 0
        ]  # Positive eigenvalues
        assert len(pos_energies) == n_sites, "Should have N positive eigenvalues"
        # assert np.all(pos_energies >= 0), "Energies should be non-negative"

        # Verify diagonalization
        H_reconstructed = eigenvecs @ eigenvals @ eigenvecs.conj().T
        assert np.allclose(H, H_reconstructed), "Diagonalization should be correct"

    @pytest.mark.example
    def test_random_matrix_ensemble(self, random_seed):
        """Test random matrix ensemble from examples.rst lines 114-146"""

        def random_gaussian_ensemble(n_sites, num_samples=20):  # Reduced for testing
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
        n_sites = 3  # Small for testing
        eigenvals = random_gaussian_ensemble(n_sites, num_samples=10)

        # Validate results
        assert len(eigenvals) == n_sites * 10, "Should have N*num_samples eigenvalues"
        assert np.all(np.isfinite(eigenvals)), "All eigenvalues should be finite"

        # Basic statistical properties
        # mean_val = np.mean(eigenvals)
        std_val = np.std(eigenvals)

        # print("mean particle eigenvalue:",mean_val)
        # print("std of the eigenvalues:",std_val)

        assert std_val > 0, "Standard deviation should be positive"


class TestAdvancedExamples:
    """Test advanced examples from docs/examples.rst"""

    @pytest.mark.example
    def test_correlation_function_analysis(self, random_seed):
        """Test correlation function analysis from examples.rst lines 154-199"""

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
                for j in range(i + 1, n_sites):
                    corr = gamma[i, j + n_sites]  # ⟨a†ᵢaⱼ⟩
                    correlations.append((j - i, abs(corr)))

            return {
                "occupations": occupations,
                "correlations": correlations,
                "gamma": gamma,
                "covariance": cov,
            }

        # Example: Uniform hopping chain
        n_sites = 4  # Small for testing
        A = np.zeros((n_sites, n_sites))
        for i in range(n_sites - 1):
            A[i, i + 1] = A[i + 1, i] = -1.0

        results = analyze_correlations(n_sites, A)

        # Validate results
        assert len(results["occupations"]) == n_sites, "Should have N occupations"
        assert np.all(results["occupations"] >= 0), "Occupations should be non-negative"
        assert np.all(results["occupations"] <= 1), "Occupations should be ≤ 1"

        # Check correlation matrix properties
        gamma = results["gamma"]
        assert gamma.shape == (2 * n_sites, 2 * n_sites), "Gamma should be 2N x 2N"

        # Check covariance matrix properties
        cov = results["covariance"]
        assert np.allclose(cov, -cov.T), "Covariance should be antisymmetric"

    @pytest.mark.example
    def test_perfect_matching_in_graphs(self, random_seed):
        """Test perfect matching example from examples.rst lines 201-246"""

        def analyze_perfect_matchings(n_vertices):
            """Analyze perfect matchings using pfaffian method."""
            if n_vertices % 2 != 0:
                return None, None, None

            # Generate random planar graph
            G = ff.generate_random_planar_graph(n_vertices, seed=42)

            if G is None:
                return None, None, None

            # Method 1: Brute force enumeration
            matchings_brute = ff.find_perfect_matchings_brute(G)

            # Method 2: Pfaffian calculation
            pfo_matrix = ff.pfo_algorithm(G, verbose=False)

            A = nx.adjacency_matrix(G).toarray()
            pfoA = np.multiply(pfo_matrix, A)
            pfoA = np.triu(pfoA)
            pfoA = pfoA - pfoA.T
            pf_value = ff.pf(pfoA)

            return G, matchings_brute, pf_value

        # Test with different sizes
        for n in [4, 6]:
            G, matchings_brute, pf_value = analyze_perfect_matchings(n)

            if G is not None:
                # Verify they match
                assert (
                    abs(len(matchings_brute) - abs(pf_value)) < 1e-10
                ), "Brute force and pfaffian methods should agree"

                # Additional validations
                assert len(G.nodes()) == n, f"Graph should have {n} nodes"
                is_planar, _ = nx.check_planarity(G)
                assert is_planar, "Graph should be planar"

    @pytest.mark.example
    def test_symplectic_transformation_example(self, random_seed):
        """Test symplectic transformation from examples.rst lines 248-291"""
        n_sites = 3

        # Create random Hamiltonian
        A = np.random.randn(n_sites, n_sites)
        A = A + A.T
        H = ff.build_H(n_sites, A)

        # Symplectic diagonalization
        L, U = ff.eigh_sp(H)

        # Validate symplectic properties
        assert ff.is_symp(U), "U should be symplectic"
        assert np.allclose(
            np.diag(L)[n_sites:], -np.diag(L)[:n_sites]
        ), "Eigenvalues should appear in +/- pairs"

        # Verify diagonalization: U† H U = L
        H_diag = U.conj().T @ H @ U

        assert np.allclose(H_diag, L), "Diagonalization should be correct"

        # Additional symplectic property tests
        # For symplectic matrices: U S U^T = S
        S = np.zeros_like(H)
        S[:n_sites, n_sites:] = np.eye(n_sites)
        S[n_sites:, :n_sites] = np.eye(n_sites)

        S_transformed = U @ S @ U.T
        assert np.allclose(S_transformed, S), "Symplectic form should be preserved"


class TestUtilityExamples:
    """Test utility examples from docs/examples.rst"""

    @pytest.mark.example
    def test_matrix_cleaning_example(self):
        """Test matrix cleaning from examples.rst lines 296-320"""
        # Create matrix with numerical noise
        clean_matrix = np.array([[1.0, 0.0, 0.5], [0.0, 2.0, 0.0], [0.5, 0.0, 1.5]])

        noise = 1e-12 * np.random.randn(3, 3)
        noisy_matrix = clean_matrix + noise

        # Clean the matrix
        cleaned = ff.clean(noisy_matrix, threshold=1e-10)

        # Validate cleaning
        assert np.allclose(
            cleaned, clean_matrix, atol=1e-10
        ), "Cleaned matrix should match original"

        # Test that small values are actually removed
        assert np.all(
            np.abs(cleaned[cleaned != 0]) >= 1e-10
        ), "No values smaller than threshold should remain"

    @pytest.mark.example
    def test_custom_printing_example(self):
        """Test custom printing from examples.rst lines 322-341"""
        # Complex matrix with varying magnitudes
        matrix = np.array([[1.23456789, 1e-8 + 2.3456j], [0.000123456, 9.87654321]])

        # Test that _print doesn't crash with various inputs
        try:
            ff.ff_utils._print(matrix, k=3)
            ff.ff_utils._print(matrix, k=6)
            # If we get here without exception, the test passes
            assert True
        except Exception as e:
            pytest.fail(f"_print should not raise exception: {e}")

        # Test with different data types
        try:
            ff.ff_utils._print(np.array([1, 2, 3]), k=2)
            ff.ff_utils._print(np.array([[1.0, 2.0], [3.0, 4.0]]), k=4)
            assert True
        except Exception as e:
            pytest.fail(f"_print should handle different array types: {e}")


class TestPerformanceExamples:
    """Test performance examples from docs/examples.rst"""

    @pytest.mark.example
    @pytest.mark.slow
    def test_large_system_benchmark(self, random_seed):
        """Test large system benchmark from examples.rst lines 349-386"""

        def benchmark_large_system(n_sites):
            """Benchmark performance for large systems."""
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
            _ = ff.generate_gaussian_state(n_sites, H, alphas)
            state_time = time.time() - start

            return {
                "h_time": h_time,
                "diag_time": diag_time,
                "state_time": state_time,
                "total_time": h_time + diag_time + state_time,
            }

        # Benchmark different sizes (smaller for testing)
        for n in [3, 5]:  # Reduced from [5, 10, 15] for faster testing
            times = benchmark_large_system(n)

            # Validate that operations completed
            assert times["h_time"] > 0, "Hamiltonian construction should take time"
            assert times["diag_time"] > 0, "Diagonalization should take time"
            assert times["state_time"] > 0, "State generation should take time"
            assert times["total_time"] > 0, "Total time should be positive"

            # Validate that times are reasonable (not too long for small systems)
            assert times["total_time"] < 10.0, "Small systems should be fast"


class TestExampleEdgeCases:
    """Test edge cases and error conditions from examples"""

    @pytest.mark.example
    def test_pfaffian_edge_cases(self):
        """Test pfaffian edge cases"""
        # Odd dimension should give 0
        A_odd = np.array([[0, 1, 2], [-1, 0, 3], [-2, -3, 0]])
        assert ff.pf(A_odd) == 0, "Pfaffian of odd matrix should be 0"

        # Empty matrix
        A_empty = np.array([]).reshape(0, 0)
        assert ff.pf(A_empty) == 1, "Pfaffian of empty matrix should be 1"

        # 2x2 identity-like
        A_2x2 = np.array([[0, 1], [-1, 0]])
        assert abs(ff.pf(A_2x2) - 1) < 1e-10, "pf([[0,1],[-1,0]]) should be 1"

    @pytest.mark.example
    def test_graph_edge_cases(self):
        """Test graph algorithm edge cases"""
        # Empty graph
        G_empty = nx.Graph()
        matchings = ff.find_perfect_matchings_brute(G_empty)
        assert len(matchings) == 1, "Empty graph has one perfect matching (empty)"

        # Single node (odd)
        G_single = nx.Graph()
        G_single.add_node(0)
        matchings = ff.find_perfect_matchings_brute(G_single)
        assert len(matchings) == 0, "Single node has no perfect matching"

        # Two disconnected nodes
        G_two = nx.Graph()
        G_two.add_nodes_from([0, 1])
        matchings = ff.find_perfect_matchings_brute(G_two)
        assert len(matchings) == 0, "Disconnected nodes have no perfect matching"

        # Two connected nodes
        G_edge = nx.Graph()
        G_edge.add_edge(0, 1)
        matchings = ff.find_perfect_matchings_brute(G_edge)
        assert len(matchings) == 1, "Single edge is one perfect matching"
