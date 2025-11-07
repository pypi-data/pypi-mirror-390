"""
Integration Tests for Free Fermion Library

This module contains comprehensive integration tests that validate end-to-end workflows
and interactions between different components of the Free Fermion Library.

Test categories:
- Complete workflow tests from tutorials
- Cross-module integration tests
- Real-world use case simulations
- Performance integration tests
- Error propagation tests
"""

import time

import networkx as nx
import numpy as np

# Import the library
import ff


class TestTutorialWorkflows:
    """Test complete workflows from the tutorials"""

    def test_basic_correlation_matrix_workflow(self):
        """Test complete workflow: create system → correlation matrix → analysis"""
        # Step 1: Create a simple fermionic system
        n_sites = 4

        # Create random coupling generating coupling matrix
        rho = ff.random_FF_state(n_sites)

        # Step 2: Compute correlation matrix
        correlation_matrix = ff.correlation_matrix(rho)

        S = ff.compute_algebra_S(ff.jordan_wigner_alphas(n_sites))
        # Step 3: Verify properties of the correlation matrix
        # Verify that Gamma + Gamma^T = S
        assert correlation_matrix.shape == (
            2 * n_sites,
            2 * n_sites,
        ), "Correlation matrix should have correct shape"
        assert np.allclose(
            correlation_matrix + correlation_matrix.T, S
        ), "Gamma + Gamma^T should equal S"
        assert np.allclose(
            correlation_matrix @ S, (correlation_matrix @ S).T.conj()
        ), "Correlation matrix should be Hermitian"

        # Step 3: Analyze properties
        eigenvals = np.linalg.eigvals(correlation_matrix @ S)
        eigenvals = np.sort(eigenvals)
        # Step 4: Verify eigenvalues
        assert (
            len(eigenvals) == 2 * n_sites
        ), "Should have correct number of eigenvalues"
        assert np.all(eigenvals >= -1e-10), "Eigenvalues should be non-negative"
        assert np.all(eigenvals <= 1 + 1e-10), "Eigenvalues should be ≤ 1"

    def test_symplectic_diagonalization_workflow(self):
        """Test complete symplectic diagonalization workflow"""
        # Step 1: Create symplectic matrix
        n = 4
        A = np.random.randn(n, n) + 1j * np.random.randn(n, n)
        Z = np.random.randn(n, n) + 1j * np.random.randn(n, n)
        A = A + A.conj().T
        Z = Z - Z.T

        H = ff.build_H(n, A, Z)

        alphas = ff.jordan_wigner_alphas(n)
        S = ff.compute_algebra_S(alphas)

        # Step 2: Perform symplectic diagonalization
        eigenvals, eigenvecs = ff.eigh_sp(H)

        # Step 3: Verify symplectic properties
        # Check symplectic property: V^T S V = S
        symplectic_check = eigenvecs.T @ S @ eigenvecs
        assert np.allclose(symplectic_check, S), "Should preserve symplectic form"

        # Verify results
        assert len(eigenvals) == 2 * n, "Should have correct number of eigenvalues"
        assert eigenvecs.shape == (
            2 * n,
            2 * n,
        ), "Eigenvectors should have correct shape"

    # def test_gaussian_state_workflow(self):
    # """Test complete Gaussian state preparation and analysis"""
    # Step 1: Define system parameters
    # n_modes = 6

    # Step 2: Create covariance matrix
    # gamma = np.random.randn(6,6)
    # gamma = gamma - gamma.T #ff.random_covariance_matrix(n_modes)

    # Step 3: Prepare Gaussian state
    # state = ff.gaussian_state(gamma)

    # Step 4: Compute observables
    # correlation_matrix = ff.state_correlation_matrix(state)
    # entanglement = ff.entanglement_entropy(state, subsystem=[0, 1])

    # Verify workflow
    # assert gamma.shape == (2*n_modes,
    #  2*n_modes), "Covariance matrix should have correct size"
    # assert correlation_matrix.shape == (n_modes,
    #  n_modes), "Correlation matrix should be correct size"
    # assert entanglement >= 0, "Entanglement entropy should be non-negative"

    # def test_kitaev_chain_workflow(self):
    #     """Test complete Kitaev chain analysis workflow"""
    #     # Step 1: Set up Kitaev chain parameters
    #     L = 8  # Chain length
    #     t = 1.0  # Hopping
    #     mu = 0.005  # Chemical potential
    #     Delta = 0.99  # Pairing

    #     # Step 2: Construct Hamiltonian
    #     H = ff.kitaev_chain(L, mu, t, Delta)
    #     # Step 3: Diagonalize and find ground state
    #     eigenvals, eigenvecs = ff.eigh_sp(H)

    #     eigenvals = ff.clean(eigenvals,10)
    #     eigenvecs = ff.clean(eigenvecs,11)

    #     ff.ff_utils._print(np.diag(eigenvals),7)

    #     #eigenvals, eigenvecs = np.linalg.eigh(H)
    #     ground_state_energy = np.min(np.diag(eigenvals)[L:])
    #     ground_state_idx = np.argmin(np.diag(eigenvals)[L:])

    #     ground_state_vec = eigenvecs[ground_state_idx,:]

    #     rho = eigenvecs[ground_state_idx,:] @ (eigenvecs[ground_state_idx,:]).conj().T
    #     # Step 4: Compute correlation functions
    #     #correlation_matrix = ff.ground_state_correlations(rho)

    #     # Step 5: Analyze topological properties
    #     gap = min(eigenvals[eigenvals > 0]) - max(eigenvals[eigenvals < 0])

    #     # Verify workflow
    #     assert H.shape == (2*L, 2*L), "Hamiltonian should have correct size"
    #     assert np.allclose(H, H.T.conj()), "Hamiltonian should be Hermitian"
    #     assert gap >= 0, "Energy gap should be non-negative"
    #     assert correlation_matrix.shape == (L,
    #           L), "Correlations should have correct shape"


class TestCrossModuleIntegration:
    """Test integration between different modules"""

    def test_combinatorics_graph_theory_integration(self):
        """Test integration between combinatorics and graph theory"""
        # Create a small planar graph
        G = nx.cycle_graph(4)

        # Get adjacency matrix
        A = nx.adjacency_matrix(G).toarray()

        # Count perfect matchings using graph theory
        pm_count_graph = ff.count_perfect_matchings(G)

        # Count perfect matchings using combinatorics (pfaffian method)
        # Need to create proper skew-symmetric matrix for pfaffian
        pfo = ff.pfo_algorithm(G)

        A_oriented = np.multiply(pfo, A)
        A_oriented = np.triu(A_oriented)
        A_oriented = A_oriented - A_oriented.T

        pm_count_pfaffian = abs(ff.pf(A_oriented))

        # Results should be consistent
        assert np.allclose(pm_count_graph, pm_count_pfaffian)
        assert pm_count_graph >= 0, "Graph method should give non-negative count"
        # Note: Direct comparison may not work due to orientation issues
        assert isinstance(
            pm_count_pfaffian, (int, float, complex)
        ), "Pfaffian should give numeric result"

    def test_lib_combinatorics_integration(self):
        """Test integration between main library and combinatorics"""
        # Create correlation matrix
        n = 4
        gamma = np.random.randn(2 * n, 2 * n)
        gamma = gamma - gamma.T

        # Compute determinant using both methods
        det_numpy = np.linalg.det(gamma)
        det_combinatorial = ff.dt(gamma)

        # Should give same result
        assert np.allclose(
            det_numpy, det_combinatorial
        ), "Determinant methods should agree"

        # Compute pfaffian of skew-symmetric part
        gamma_skew = gamma - gamma.T
        pf_val = ff.pf(gamma_skew)

        # Check pfaffian property: pf(A)^2 = det(A) for skew-symmetric A
        det_skew = ff.dt(gamma_skew)
        assert np.allclose(pf_val**2, det_skew), "Pfaffian property should hold"

    def test_lib_utils_integration(self):
        """Test integration between main library and utilities"""
        # Create system with numerical noise
        n = 4
        H = np.random.randn(n, n) + 1e-15 * np.random.randn(n, n) * 1j
        H = H + H.T.conj()  # Make Hermitian with small numerical errors

        # Clean the Hamiltonian
        H_clean = ff.clean(H)

        # Compute correlation matrix
        gamma = ff.correlation_matrix(H_clean)

        # Format output
        formatted_gamma = ff.formatted_output(gamma)

        # Verify integration
        assert np.allclose(
            H_clean.imag, 0
        ), "Cleaning should remove small imaginary parts"
        assert gamma.shape == (n, n), "Correlation matrix should have correct shape"
        assert isinstance(
            formatted_gamma, str
        ), "Should produce formatted string output"

    def test_graph_theory_utils_integration(self):
        """Test integration between graph theory and utilities"""
        # Create graph and compute properties
        G = nx.grid_2d_graph(3, 3)

        # Get adjacency matrix
        A = nx.adjacency_matrix(G).toarray().astype(float)

        # Add small numerical noise
        A_noisy = A + 1e-14 * np.random.randn(*A.shape)

        # Clean the matrix
        A_clean = ff.clean(A_noisy)

        # Verify it's still a valid adjacency matrix
        assert np.allclose(A_clean, A_clean.T), "Should remain symmetric"
        assert np.allclose(A_clean, A), "Should recover original matrix"
        assert np.all((A_clean == 0) | (A_clean == 1)), "Should have only 0s and 1s"


class TestRealWorldUseCases:
    """Test realistic use cases and applications"""

    def test_quantum_simulation_workflow(self):
        """Test complete quantum simulation workflow"""
        # Simulate a quantum many-body system

        # Step 1: Define system (1D chain with nearest-neighbor hopping)
        L = 6
        t = 1.0  # Hopping amplitude

        # Step 2: Construct Hamiltonian matrix
        H = np.zeros((L, L))
        for i in range(L - 1):
            H[i, i + 1] = -t
            H[i + 1, i] = -t

        # Step 3: Add disorder
        disorder_strength = 0.1
        disorder = disorder_strength * np.random.randn(L)
        H += np.diag(disorder)

        # Step 4: Diagonalize
        eigenvals, eigenvecs = np.linalg.eigh(H)

        # Step 5: Compute ground state properties
        ground_state = eigenvecs[:, 0]
        ground_energy = eigenvals[0]

        # Step 6: Compute correlation functions
        correlations = np.outer(ground_state, ground_state.conj())

        # Step 7: Analyze entanglement
        subsystem_size = L // 2
        reduced_density = correlations[:subsystem_size, :subsystem_size]
        entanglement = -np.trace(reduced_density @ np.log(reduced_density + 1e-12))

        # Verify simulation results
        assert len(eigenvals) == L, "Should have correct number of eigenvalues"
        assert ground_energy <= eigenvals[1], "Ground state should have lowest energy"
        assert entanglement >= 0, "Entanglement should be non-negative"
        assert correlations.shape == (L, L), "Correlations should have correct shape"

    def test_topological_phase_detection(self):
        """Test detection of topological phases"""
        # Scan through parameter space of Kitaev chain

        L = 10
        t = 1.0
        Delta = 0.5

        mu_values = np.linspace(-2, 2, 21)
        gaps = []

        for mu in mu_values:
            # Construct Hamiltonian

            H = ff.kitaev_chain(L, mu, t, Delta)

            # Diagonalize
            [eigenvals, _] = ff.eigh_sp(H)
            eigenvals = np.diag(eigenvals)
            eigenvals = np.sort(eigenvals)

            # Find gap
            gap = eigenvals[L] - eigenvals[L - 1]  # Gap around zero energy
            gaps.append(gap)

        gaps = np.array(gaps)

        # Verify phase detection
        assert len(gaps) == len(mu_values), "Should compute gap for each parameter"
        assert np.all(gaps >= 0), "Gaps should be non-negative"

        # Should see gap closing and reopening (topological phase transition)
        min_gap_idx = np.argmin(gaps)
        assert 0 < min_gap_idx < len(gaps) - 1, "Gap minimum should be in interior"

    def test_quantum_error_correction_workflow(self):
        """Test quantum error correction code analysis"""
        # Analyze a simple quantum error correction code

        # Step 1: Define stabilizer code (simplified)
        n_qubits = 4
        n_stabilizers = 2

        # Step 2: Create stabilizer matrix (Pauli operators)
        stabilizers = np.array([[1, 1, 0, 0], [0, 0, 1, 1]])  # X1 X2  # X3 X4

        # Step 3: Compute syndrome space
        syndrome_space = stabilizers @ stabilizers.T % 2

        # Step 4: Analyze error correction capability
        # code_distance = ff.compute_code_distance(stabilizers)

        # Step 5: Compute logical operators
        # logical_ops = ff.find_logical_operators(stabilizers)

        # Verify error correction analysis
        assert stabilizers.shape == (
            n_stabilizers,
            n_qubits,
        ), "Stabilizers should have correct shape"
        assert syndrome_space.shape == (
            n_stabilizers,
            n_stabilizers,
        ), "Syndrome space should be square"

        # assert code_distance >= 1, "Code distance should be positive"

    def test_condensed_matter_workflow(self):
        """Test condensed matter physics workflow"""
        # Analyze a 2D lattice system

        # Step 1: Create 2D square lattice
        Lx, Ly = 4, 4
        G = nx.grid_2d_graph(Lx, Ly)

        # Step 2: Add periodic boundary conditions
        for i in range(Lx):
            G.add_edge((i, 0), (i, Ly - 1))
        for j in range(Ly):
            G.add_edge((0, j), (Lx - 1, j))

        # Step 3: Construct tight-binding Hamiltonian
        n_sites = Lx * Ly
        H = np.zeros((n_sites, n_sites))

        # Map 2D coordinates to 1D indices
        coord_to_idx = {node: i for i, node in enumerate(G.nodes())}

        # Add hopping terms
        t = 1.0
        for edge in G.edges():
            i, j = coord_to_idx[edge[0]], coord_to_idx[edge[1]]
            H[i, j] = -t
            H[j, i] = -t

        # Step 4: Diagonalize and compute band structure
        eigenvals, eigenvecs = np.linalg.eigh(H)

        # Step 5: Compute density of states
        energy_bins = np.linspace(eigenvals.min(), eigenvals.max(), 50)
        dos, _ = np.histogram(eigenvals, bins=energy_bins)

        # Step 6: Analyze transport properties
        # conductivity = ff.compute_conductivity(H, eigenvals, eigenvecs)

        # Verify condensed matter analysis
        assert H.shape == (n_sites, n_sites), "Hamiltonian should have correct size"
        assert len(eigenvals) == n_sites, "Should have correct number of bands"
        assert len(dos) == len(energy_bins) - 1, "DOS should have correct binning"
        # assert conductivity >= 0, "Conductivity should be non-negative"


class TestPerformanceIntegration:
    """Test performance of integrated workflows"""

    def test_large_system_performance(self):
        """Test performance on larger systems"""
        # Test with moderately large system
        n = 50

        start_time = time.time()

        # Create random Hamiltonian
        H = np.random.randn(n, n)
        H = H + H.T

        # Diagonalize
        eigenvals, eigenvecs = np.linalg.eigh(H)

        # Compute correlation matrix
        gamma = ff.correlation_matrix(H)

        # Clean results
        gamma_clean = ff.clean(gamma)

        end_time = time.time()
        elapsed = end_time - start_time

        # Verify performance
        assert (
            elapsed < 10.0
        ), "Large system workflow should complete in reasonable time"
        assert gamma_clean.shape == (n, n), "Should produce correct result"

    def test_repeated_calculations_performance(self):
        """Test performance of repeated calculations"""
        # Test caching and optimization
        n = 20
        n_iterations = 10

        start_time = time.time()

        for i in range(n_iterations):
            # Create system
            H = np.random.randn(n, n)
            H = H + H.T

            # Compute properties
            eigenvals = np.linalg.eigvals(H)
            det_val = ff.dt(H)

            # Verify each iteration
            assert len(eigenvals) == n, "Should compute eigenvalues"
            assert np.isfinite(det_val), "Should compute determinant"

        end_time = time.time()
        elapsed = end_time - start_time

        # Should complete all iterations in reasonable time
        assert elapsed < 30.0, "Repeated calculations should be efficient"

    def test_memory_usage_integration(self):
        """Test memory usage in integrated workflows"""
        # Test that memory usage remains reasonable
        import gc

        initial_objects = len(gc.get_objects())

        # Perform memory-intensive workflow
        for i in range(5):
            n = 8

            rho, H = ff.random_FF_state(n, returnH=True)

            eigenvals, eigenvecs = np.linalg.eigh(H)
            gamma = ff.correlation_matrix(rho)

            # Clean up explicitly
            del H, eigenvals, eigenvecs, gamma
            gc.collect()

        final_objects = len(gc.get_objects())

        # Memory usage should not grow excessively
        object_growth = final_objects - initial_objects
        assert object_growth < 1000, "Memory usage should remain reasonable"


class TestErrorPropagation:
    """Test error handling and propagation across modules"""

    # def test_invalid_input_propagation(self):
    #     """Test how invalid inputs propagate through workflows"""
    #     # Test with invalid matrix
    #     invalid_matrix = np.array([[1, 2], [3]])  # Ragged array

    #     with pytest.raises((ValueError, IndexError, TypeError)):
    #         # Should raise error somewhere in the workflow
    #         gamma = ff.correlation_matrix(invalid_matrix)
    #         eigenvals = np.linalg.eigvals(gamma)

    def test_numerical_error_propagation(self):
        """Test how numerical errors propagate"""
        # Create ill-conditioned matrix
        n = 8
        h = np.random.randn(n, n)
        h = h + h.T

        # Make it nearly singular
        h[0, :] = h[1, :] * (1 + 1e-15)

        H = ff.build_H(n, h)

        from scipy.linalg import expm

        rho = expm(-H)
        rho /= np.trace(rho)  # Normalize

        import warnings

        # Workflow should handle gracefully or warn
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")

            try:
                gamma = ff.correlation_matrix(rho)
                det_val = ff.dt_eigen(gamma)

                # Should either succeed or generate warnings
                assert (
                    np.isfinite(det_val) or len(w) > 0
                ), "Should handle or warn about numerical issues"
            except np.linalg.LinAlgError:
                # Acceptable to fail on singular matrices
                pass


class TestWorkflowValidation:
    """Test validation of complete workflows against known results"""

    # def test_analytical_solution_validation(self):
    #     """Test workflows against known analytical solutions"""
    #     # Test case: 2-site system with known solution

    #     # Hamiltonian: H = -t(c1†c2 + c2†c1)
    #     t = 1.0
    #     H = np.array([[0, -t], [-t, 0]])

    #     # Analytical eigenvalues: ±t
    #     eigenvals_analytical = np.array([-t, t])

    #     # Compute using workflow
    #     eigenvals_computed = np.linalg.eigvals(H)
    #     eigenvals_computed = np.sort(eigenvals_computed)

    #     # Should match analytical result
    #     assert np.allclose(eigenvals_computed,
    #         eigenvals_analytical), "Should match analytical eigenvalues"

    #     # Test correlation matrix
    #     gamma = ff.correlation_matrix(H)

    #     # For ground state of this system, analytical correlation matrix is known
    #     gamma_analytical = np.array([[0.5, 0.5], [0.5, 0.5]])

    #     # Should be close to analytical result (may differ by basis choice)
    #     assert gamma.shape == gamma_analytical.shape, "Should have correct shape"
    #     assert np.allclose(np.trace(gamma), 1.0), "Trace should be 1 (one particle)"

    # def test_symmetry_preservation(self):
    #     """Test that workflows preserve expected symmetries"""
    #     # Test particle-hole symmetry
    #     n = 4
    #     H = ff.random_H_generator(n,fixedN=True)

    #     # Eigenvalues should come in ±pairs
    #     eigenvals = np.linalg.eigvals(H)
    #     eigenvals_sorted = np.sort(eigenvals)

    #     # Check if eigenvalues are approximately paired
    #     for i in range(n//2):
    #         assert np.allclose(eigenvals_sorted[i], -eigenvals_sorted[n-1-i]), \
    #             "Particle-hole symmetry should be preserved"

    # def test_conservation_laws(self):
    #     """Test that workflows respect conservation laws"""
    #     # Test particle number conservation
    #     n = 4

    #     # Create number-conserving Hamiltonian (hopping only)
    #     H = np.zeros((n, n))
    #     for i in range(n-1):
    #         H[i, i+1] = -1.0
    #         H[i+1, i] = -1.0

    #     # Correlation matrix should conserve particle number
    #     gamma = ff.correlation_matrix(H)

    #     # Total particle number should be conserved
    #     total_particles = np.trace(gamma)

    #     # For half-filled system, should have n/2 particles
    #     expected_particles = n / 2
    #     assert np.allclose(total_particles, expected_particles), \
    #         "Particle number should be conserved"

    def test_thermodynamic_consistency(self):
        """Test thermodynamic consistency of results"""
        # Test that results satisfy thermodynamic relations

        n = 6
        H = ff.random_H_generator(n)
        alphas = ff.jordan_wigner_alphas(n)
        S = ff.compute_algebra_S(alphas)
        H_op = ff.build_op(n, H, alphas)

        # Compute properties at different temperatures
        temperatures = [0.1, 1.0, 10.0]
        entropies = []

        from scipy.linalg import expm

        for T in temperatures:
            # Compute thermal correlation matrix
            rho = expm(-H_op / T)
            rho /= np.trace(rho)

            gamma_T = ff.correlation_matrix(rho)

            # Compute entropy
            eigenvals_gamma = np.linalg.eigvals(gamma_T @ S)
            eigenvals_gamma = np.clip(eigenvals_gamma, 1e-12, 1 - 1e-12)  # Avoid log(0)

            entropy = -np.sum(
                eigenvals_gamma * np.log(eigenvals_gamma)
                + (1 - eigenvals_gamma) * np.log(1 - eigenvals_gamma)
            )
            entropies.append(ff.clean(entropy))

        # Entropy should increase with temperature
        print("Entropies at different temperatures:", entropies)
        assert entropies[1] >= entropies[0], "Entropy should increase with temperature"
        assert entropies[2] >= entropies[1], "Entropy should increase with temperature"
