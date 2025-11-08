"""
Core Library Tests for Free Fermion Library

This module contains comprehensive tests for the core functionality in ff_lib.py,
including Jordan-Wigner operators, matrix construction, symplectic operations,
and Gaussian state generation.

Test categories:
- Jordan-Wigner Operators (alphas, majoranas, lowering)
- Matrix Construction (build_H, build_V, build_Omega)
- Symplectic Operations (eigh_sp, is_symp, check_canonical_form)
- Gaussian States (generate_gaussian_state, correlation matrices)
- Operator Rotations and Transformations
"""

import numpy as np

# Import the library
import ff


class TestJordanWignerOperators:
    """Test Jordan-Wigner operator construction and properties"""

    def test_jordan_wigner_alphas_basic(self):
        """Test basic properties of Jordan-Wigner alpha operators"""
        n_sites = 3
        alphas = ff.jordan_wigner_alphas(n_sites)

        # Should have 2N operators (N raising + N lowering)
        assert len(alphas) == 2 * n_sites, "Should have 2N operators"

        # Each operator should be 2^N x 2^N
        expected_dim = 2**n_sites
        for alpha in alphas:
            assert alpha.shape == (
                expected_dim,
                expected_dim,
            ), f"Operators should be {expected_dim}x{expected_dim}"

        # First N operators are raising, last N are lowering
        # Raising operators should be Hermitian conjugates of lowering
        for i in range(n_sites):
            raising = alphas[i]
            lowering = alphas[i + n_sites]
            assert np.allclose(
                raising, lowering.conj().T
            ), "Raising operators should be adjoints of lowering operators"

    def test_jordan_wigner_lowering(self):
        """Test Jordan-Wigner lowering operators"""
        n_sites = 2
        lowering = ff.jordan_wigner_lowering(n_sites)

        assert len(lowering) == n_sites, "Should have N lowering operators"

        # Test that operators have correct dimensions
        expected_dim = 2**n_sites
        for op in lowering:
            assert op.shape == (
                expected_dim,
                expected_dim,
            ), f"Operators should be {expected_dim}x{expected_dim}"

        # Test specific matrix elements for 2-site case
        # a_0 should annihilate |00⟩ and |01⟩, transform |10⟩→|00⟩, |11⟩→|01⟩
        a0 = lowering[0]
        a1 = lowering[1]

        vac = np.zeros((2**n_sites, 1))
        vac[0] = 1

        # In computational basis: |00⟩, |01⟩, |10⟩, |11⟩
        assert np.allclose(a0 @ vac, 0), "a_0|00⟩ = 0"
        assert np.allclose(a0 @ a0.conj().T @ vac - vac, 0), "a_0|10⟩ = |00⟩"

        state11 = a0.conj().T @ a1.conj().T @ vac
        state10 = a0.conj().T @ vac

        assert np.allclose(
            a1 @ state11 + state10, 0
        ), "a_1|11⟩ = -|10⟩ (with Jordan-Wigner string)"

    def test_jordan_wigner_majoranas(self):
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

        # Test that they square to identity (up to normalization)
        for gamma in majoranas:
            gamma_squared = gamma @ gamma
            # Should be proportional to identity
            trace_ratio = np.trace(gamma_squared) / gamma_squared.shape[0]
            identity_scaled = trace_ratio * np.eye(gamma_squared.shape[0])
            assert np.allclose(
                gamma_squared, identity_scaled, atol=1e-10
            ), "Majorana operators should square to (scaled) identity"

    def test_anticommutation_relations(self):
        """Test fermionic anticommutation relations"""
        n_sites = 2
        alphas = ff.jordan_wigner_alphas(n_sites)

        # Test canonical anticommutation relations
        # {a_i, a_j†} = δ_ij, {a_i, a_j} = 0, {a_i†, a_j†} = 0
        for i in range(n_sites):
            for j in range(n_sites):
                # {a_i, a_j†} = a_i a_j† + a_j† a_i
                ai = alphas[i + n_sites]  # lowering
                aj_dag = alphas[j]  # raising

                anticomm = ai @ aj_dag + aj_dag @ ai

                if i == j:
                    # Should be identity
                    assert np.allclose(
                        anticomm, np.eye(anticomm.shape[0])
                    ), f"{{a_{i}, a_{j}†}} should be identity when i=j"
                else:
                    # Should be zero
                    assert np.allclose(
                        anticomm, np.zeros_like(anticomm)
                    ), f"{{a_{i}, a_{j}†}} should be zero when i≠j"


class TestMatrixConstruction:
    """Test matrix construction functions"""

    def test_build_H_basic(self):
        """Test basic Hamiltonian matrix construction"""
        n_sites = 2
        A = np.array([[1.0, 0.5], [0.5, 1.0]])

        H = ff.build_H(n_sites, A)

        # Check dimensions
        assert H.shape == (4, 4), "H should be 2N x 2N"

        # Check block structure: H = [[-A*, B], [-B*, A]]
        # When B is not provided, it defaults to zeros
        assert np.allclose(
            H[:n_sites, :n_sites], -A.conj()
        ), "Top-left block should be -A*"
        assert np.allclose(
            H[:n_sites, n_sites:], np.zeros((n_sites, n_sites))
        ), "Top-right block should be zero when B not provided"
        assert np.allclose(
            H[n_sites:, :n_sites], np.zeros((n_sites, n_sites))
        ), "Bottom-left block should be zero when B not provided"
        assert np.allclose(H[n_sites:, n_sites:], A), "Bottom-right block should be A"

    def test_build_H_with_pairing(self):
        """Test Hamiltonian construction with pairing term"""
        n_sites = 2
        A = np.array([[1.0, 0.5], [0.5, 1.0]])
        B = np.array([[0, 0.2], [-0.2, 0]])

        H = ff.build_H(n_sites, A, B)

        # Check block structure with pairing
        assert np.allclose(
            H[:n_sites, :n_sites], -A.conj()
        ), "Top-left block should be -A*"
        assert np.allclose(H[:n_sites, n_sites:], B), "Top-right block should be B"
        assert np.allclose(
            H[n_sites:, :n_sites], -B.conj()
        ), "Bottom-left block should be -B*"
        assert np.allclose(H[n_sites:, n_sites:], A), "Bottom-right block should be A"

    def test_build_V(self):
        """Test generator matrix construction"""
        n_sites = 2
        A = np.array([[1.0, 0.5], [0.5, 1.0]])

        V = ff.build_V(n_sites, A)

        # Check dimensions
        assert V.shape == (4, 4), "V should be 2N x 2N"

        # Check block structure: V = [[-Z*, A], [-A*, Z]]
        # When Z is not provided, it defaults to zeros
        assert np.allclose(
            V[:n_sites, :n_sites], np.zeros((n_sites, n_sites))
        ), "Top-left block should be zero when Z not provided"
        assert np.allclose(V[:n_sites, n_sites:], A), "Top-right block should be A"
        assert np.allclose(
            V[n_sites:, :n_sites], -A.conj()
        ), "Bottom-left block should be -A*"
        assert np.allclose(
            V[n_sites:, n_sites:], np.zeros((n_sites, n_sites))
        ), "Bottom-right block should be zero when Z not provided"

    def test_build_Omega(self):
        """Test Omega matrix construction"""
        N = 3
        Omega = ff.build_Omega(N)

        # Check dimensions
        assert Omega.shape == (2 * N, 2 * N), "Omega should be 2N x 2N"

        # Check structure: Omega = (1/√2) * [[Id, Id], [i*Id, -i*Id]]
        nu = 1 / np.sqrt(2)
        expected_Omega = np.zeros((2 * N, 2 * N), dtype=complex)
        expected_Omega[:N, :N] = nu * np.eye(N)
        expected_Omega[:N, N:] = nu * np.eye(N)
        expected_Omega[N:, :N] = 1j * nu * np.eye(N)
        expected_Omega[N:, N:] = -1j * nu * np.eye(N)

        assert np.allclose(
            Omega, expected_Omega
        ), "Omega should match expected structure"

        # Test that Omega is unitary: Ω† Ω = I
        Omega_dag = Omega.conj().T
        identity = Omega_dag @ Omega
        assert np.allclose(identity, np.eye(2 * N)), "Omega should be unitary"

    def test_build_reordering_xx_to_xp(self):
        """Test reordering matrix construction"""
        n_sites = 3
        P = ff.build_reordering_xx_to_xp(n_sites)

        # Check dimensions
        assert P.shape == (2 * n_sites, 2 * n_sites), "P should be 2N x 2N"

        # Check that it's a permutation matrix (orthogonal with 0,1 entries)
        assert np.allclose(P @ P.T, np.eye(2 * n_sites)), "P should be orthogonal"
        assert np.all((P == 0) | (P == 1)), "P should have only 0,1 entries"

        # Check that each row and column has exactly one 1
        assert np.allclose(np.sum(P, axis=0), 1), "Each column should sum to 1"
        assert np.allclose(np.sum(P, axis=1), 1), "Each row should sum to 1"


class TestSymplecticOperations:
    """Test symplectic matrix operations and diagonalization"""

    def test_is_symp_canonical_form(self):
        """Test symplectic property checking for canonical form"""

        # Create a matrix in canonical symplectic form: U = [[s, t*], [t, s*]]
        s = np.array([[1, 0], [0, -1]]) / np.sqrt(2)
        t = np.array([[0, 1], [1, 0]]) / np.sqrt(2)

        U = np.block([[s, t.conj()], [t, s.conj()]])
        np.set_printoptions(linewidth=250)

        assert ff.is_symp(U), "Canonical unitary form matrix should be symplectic"

    def test_check_canonical_form(self):
        """Test canonical form checking"""
        # Create a matrix in canonical form: block diagonal with 2x2 blocks
        L = np.array([[0, -1, 0, 0], [1, 0, 0, 0], [0, 0, 0, -2], [0, 0, 2, 0]])

        assert ff.check_canonical_form(L), "Matrix should be in canonical form"

        # Test non-canonical form
        L_bad = np.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]])

        assert not ff.check_canonical_form(
            L_bad
        ), "Diagonal matrix should not be canonical"

    def test_eigh_sp_basic(self):
        """Test symplectic eigenvalue decomposition"""
        n_sites = 2

        # Create a simple Hermitian A matrix
        A = np.array([[1.0, 0.5], [0.5, 1.0]])
        H = ff.build_H(n_sites, A)

        # Perform symplectic diagonalization
        eigenvals, eigenvecs = ff.eigh_sp(H)

        # Check that eigenvectors are symplectic
        assert ff.is_symp(eigenvecs), "Eigenvectors should be symplectic"

        # Check that eigenvalues appear as np.block([Sigma, 0], [0,-Sigma])
        assert np.allclose(
            np.diag(eigenvals)[n_sites:], -np.diag(eigenvals)[:n_sites]
        ), "Eigenvalues should appear in +/- pairs"

        # Check that diagonalization is correct: U† H U = L
        H_diag = eigenvecs.conj().T @ H @ eigenvecs
        assert np.allclose(H_diag, eigenvals), "Diagonalization should be correct"

        # Check dimensions
        assert eigenvals.shape == (2 * n_sites, 2 * n_sites), "L should be 2N x 2N"
        assert eigenvecs.shape == (2 * n_sites, 2 * n_sites), "U should be 2N x 2N"

    def test_eigh_sp_with_pairing(self):
        """Test symplectic diagonalization with pairing terms"""
        n_sites = 2
        A = np.array([[1.0, 0.5], [0.5, 1.0]])
        B = np.array([[0, 0.2], [-0.2, 0]])

        H = ff.build_H(n_sites, A, B)
        eigenvals, eigenvecs = ff.eigh_sp(H)

        # Same tests as basic case
        assert ff.is_symp(eigenvecs), "Eigenvectors should be symplectic"
        # Check that eigenvalues appear as np.block([Sigma, 0], [0,-Sigma])
        assert np.allclose(
            np.diag(eigenvals)[n_sites:], -np.diag(eigenvals)[:n_sites]
        ), "Eigenvalues should appear in +/- pairs"

        H_diag = eigenvecs.conj().T @ H @ eigenvecs
        assert np.allclose(H_diag, eigenvals), "Diagonalization should be correct"


class TestGaussianStates:
    """Test Gaussian state generation and correlation matrices"""

    def test_generate_gaussian_state_basic(self):
        """Test basic Gaussian state generation"""
        n_sites = 2
        A = np.array([[1.0, 0.5], [0.5, 1.0]])
        H = ff.build_H(n_sites, A)
        alphas = ff.jordan_wigner_alphas(n_sites)

        rho = ff.generate_gaussian_state(n_sites, H, alphas)

        # Check dimensions
        expected_dim = 2**n_sites
        assert rho.shape == (
            expected_dim,
            expected_dim,
        ), f"State should be {expected_dim}x{expected_dim}"

        # Check normalization
        assert np.allclose(np.trace(rho), 1.0), "State should be normalized"

        # Check that it's positive semidefinite
        eigenvals = np.linalg.eigvals(rho)
        assert np.all(eigenvals >= -1e-10), "State should be positive semidefinite"

        # Check that it's Hermitian
        assert np.allclose(rho, rho.conj().T), "State should be Hermitian"

    def test_compute_2corr_matrix(self):
        """Test two-point correlation matrix computation"""
        n_sites = 2
        A = np.array([[1.0, 0.5], [0.5, 1.0]])
        H = ff.build_H(n_sites, A)
        alphas = ff.jordan_wigner_alphas(n_sites)

        rho = ff.generate_gaussian_state(n_sites, H, alphas)
        gamma = ff.compute_2corr_matrix(rho, n_sites, alphas)

        # Check dimensions
        assert gamma.shape == (2 * n_sites, 2 * n_sites), "Gamma should be 2N x 2N"

        # Check that diagonal elements are real (occupation numbers)
        gamma_diag = np.diag(gamma)
        assert np.allclose(gamma_diag.imag, 0), "Diagonal should be real"

        # Check that occupation numbers are between 0 and 1
        occupations = gamma_diag[n_sites:]  # ⟨a†_i a_i⟩
        assert np.all(occupations >= -1e-10), "Occupations should be non-negative"
        assert np.all(occupations <= 1 + 1e-10), "Occupations should be ≤ 1"

    def test_compute_cov_matrix(self):
        """Test covariance matrix computation"""
        n_sites = 2
        A = np.array([[1.0, 0.5], [0.5, 1.0]])
        H = ff.build_H(n_sites, A)
        alphas = ff.jordan_wigner_alphas(n_sites)

        rho = ff.generate_gaussian_state(n_sites, H, alphas)
        cov = ff.compute_cov_matrix(rho, n_sites, alphas)

        # Check dimensions
        assert cov.shape == (2 * n_sites, 2 * n_sites), "Covariance should be 2N x 2N"

        # Check antisymmetry: K_ij = -K_ji
        assert np.allclose(cov, -cov.T), "Covariance should be antisymmetric"

        # Check that diagonal is zero (follows from antisymmetry)
        assert np.allclose(np.diag(cov), 0), "Diagonal should be zero"

    def test_correlation_matrix_conjugation_modes(self):
        """Test different conjugation modes for correlation matrices"""
        n_sites = 2
        A = np.array([[1.0, 0.5], [0.5, 1.0]])
        H = ff.build_H(n_sites, A)
        alphas = ff.jordan_wigner_alphas(n_sites)

        rho = ff.generate_gaussian_state(n_sites, H, alphas)

        # Test different conjugation modes
        gamma_default = ff.compute_2corr_matrix(rho, n_sites, alphas)
        gamma_positive = ff.compute_2corr_matrix(rho, n_sites, alphas, conjugation=True)
        gamma_negative = ff.compute_2corr_matrix(rho, n_sites, alphas, conjugation=-1)

        # All should have the same dimensions
        assert gamma_default.shape == gamma_positive.shape == gamma_negative.shape

        # They should be different matrices (unless special case)
        # At least one should be different
        assert not (
            np.allclose(gamma_default, gamma_positive)
            and np.allclose(gamma_default, gamma_negative)
        )


class TestOperatorRotations:
    """Test operator rotation and transformation functions"""

    def test_rotate_operators_basic(self):
        """Test basic operator rotation"""
        n_sites = 2
        alphas = ff.jordan_wigner_alphas(n_sites)

        # Create a simple rotation matrix (identity)
        C = np.eye(2 * n_sites)

        rotated_alphas = ff.rotate_operators(C, alphas)

        # Should be the same as original
        for i, (orig, rot) in enumerate(zip(alphas, rotated_alphas)):
            assert np.allclose(
                orig, rot
            ), f"Operator {i} should be unchanged by identity"

    def test_rotate_operators_unitary(self):
        """Test operator rotation with unitary matrix"""
        n_sites = 2
        alphas = ff.jordan_wigner_alphas(n_sites)

        # Create a simple unitary rotation (swap first two operators)
        C = np.eye(2 * n_sites)
        C[0, 0] = 0
        C[1, 1] = 0
        C[0, 1] = 1
        C[1, 0] = 1

        rotated_alphas = ff.rotate_operators(C, alphas)

        # First and second operators should be swapped
        assert np.allclose(
            rotated_alphas[0], alphas[1]
        ), "First operator should become second"
        assert np.allclose(
            rotated_alphas[1], alphas[0]
        ), "Second operator should become first"

        # Others should be unchanged
        for i in range(2, len(alphas)):
            assert np.allclose(
                rotated_alphas[i], alphas[i]
            ), f"Operator {i} should be unchanged"

    def test_build_op(self):
        """Test building N-body operators from coefficient matrices"""
        n_sites = 2
        alphas = ff.jordan_wigner_alphas(n_sites)

        # Create a simple coefficient matrix
        R = np.eye(2 * n_sites)

        # Build the operator
        R_op = ff.build_op(n_sites, R, alphas)

        # Check dimensions
        expected_dim = 2**n_sites
        assert R_op.shape == (
            expected_dim,
            expected_dim,
        ), f"Operator should be {expected_dim}x{expected_dim}"

        # For identity coefficient matrix, should get sum of α†_i α_i
        # This should be the number operator
        expected_op = sum(alphas[i].conj().T @ alphas[i] for i in range(2 * n_sites))
        assert np.allclose(R_op, expected_op), "Should match expected number operator"


class TestSpecialFunctions:
    """Test special functions and utilities in ff_lib"""

    def test_permutation_to_matrix(self):
        """Test permutation to matrix conversion"""
        # Simple permutation: [1, 0, 2] (swap first two elements)
        perm = [1, 0, 2]
        P = ff.permutation_to_matrix(perm)

        expected = np.array([[0, 1, 0], [1, 0, 0], [0, 0, 1]])

        assert np.allclose(P, expected), "Permutation matrix should match expected"

        # Test that it's a valid permutation matrix
        assert np.allclose(P @ P.T, np.eye(3)), "Should be orthogonal"
        assert np.allclose(np.sum(P, axis=0), 1), "Each column should sum to 1"
        assert np.allclose(np.sum(P, axis=1), 1), "Each row should sum to 1"

    def test_pauli_matrices(self):
        """Test Pauli matrix definitions"""
        sigma_x, sigma_y, sigma_z = ff.pauli_matrices()

        # Check dimensions
        for sigma in [sigma_x, sigma_y, sigma_z]:
            assert sigma.shape == (2, 2), "Pauli matrices should be 2x2"

        # Check specific values
        assert np.allclose(sigma_x, np.array([[0, 1], [1, 0]])), "σ_x should be correct"
        assert np.allclose(
            sigma_y, np.array([[0, -1j], [1j, 0]])
        ), "σ_y should be correct"
        assert np.allclose(
            sigma_z, np.array([[1, 0], [0, -1]])
        ), "σ_z should be correct"

        # Check that they square to identity
        for sigma in [sigma_x, sigma_y, sigma_z]:
            assert np.allclose(
                sigma @ sigma, np.eye(2)
            ), "Pauli matrices should square to I"

    def test_is_matchgate(self):
        """Test matchgate condition checking"""
        # Create a 4x4 matrix that satisfies matchgate condition
        # det(inner 2x2) = det(corner 2x2)
        # M = np.array([[1, 0, 0, 2], [0, 3, 4, 0], [0, 5, 6, 0], [7, 0, 0, 8]])

        # For this to be matchgate: det([[3,4],[5,6]]) = det([[1,2],[7,8]])
        # 3*6 - 4*5 = 18 - 20 = -2
        # 1*8 - 2*7 = 8 - 14 = -6
        # This doesn't satisfy matchgate, so let's create one that does

        M_good = np.array([[1, 0, 0, 2], [0, 2, 3, 0], [0, 4, 6, 0], [3, 0, 0, 6]])
        # det([[2,3],[4,6]]) = 12 - 12 = 0
        # det([[1,2],[3,6]]) = 6 - 6 = 0
        # Both determinants are 0, so this satisfies matchgate condition

        assert ff.is_matchgate(M_good), "Matrix should satisfy matchgate condition"

        # Test wrong size
        M_wrong_size = np.array([[1, 2], [3, 4]])
        assert not ff.is_matchgate(M_wrong_size), "Wrong size should return False"


class TestHaarRandomFunctions:
    """Test Haar random free-fermion functions"""

    def test_random_FF_rotation_basic(self):
        """Test basic properties of random_FF_rotation"""
        n_sites = 2

        # Test that function returns a unitary matrix
        U = ff.random_FF_rotation(n_sites, seed=42)

        # Check dimensions
        expected_dim = 2**n_sites
        assert U.shape == (
            expected_dim,
            expected_dim,
        ), f"Should be {expected_dim}x{expected_dim}"

        # Check unitarity: U† U = I
        U_dag = U.conj().T
        identity = U_dag @ U
        assert np.allclose(identity, np.eye(expected_dim)), "Should be unitary"

    def test_random_FF_rotation_reproducibility(self):
        """Test that random_FF_rotation is reproducible with seed"""
        n_sites = 2

        U1 = ff.random_FF_rotation(n_sites, seed=123)
        U2 = ff.random_FF_rotation(n_sites, seed=123)

        assert np.allclose(U1, U2), "Should be reproducible with same seed"

    def test_random_FF_rotation_returnH(self):
        """Test random_FF_rotation with returnH=True"""
        n_sites = 2

        H_op = ff.random_FF_rotation(n_sites, seed=42, returnH=True)

        # Check dimensions
        expected_dim = 2**n_sites
        assert H_op.shape == (
            expected_dim,
            expected_dim,
        ), f"Hamiltonian should be {expected_dim}x{expected_dim}"

        # Check that it's Hermitian
        assert np.allclose(H_op, H_op.conj().T), "Hamiltonian should be Hermitian"

    def test_random_FF_state_basic(self):
        """Test basic properties of random_FF_state"""
        n_sites = 2

        # Test mixed state (default)
        rho = ff.random_FF_state(n_sites, seed=42)

        # Check dimensions
        expected_dim = 2**n_sites
        assert rho.shape == (
            expected_dim,
            expected_dim,
        ), f"State should be {expected_dim}x{expected_dim}"

        # Check normalization
        assert np.allclose(np.trace(rho), 1.0), "State should be normalized"

        # Check that it's positive semidefinite
        eigenvals = np.linalg.eigvals(rho)
        assert np.all(eigenvals >= -1e-10), "State should be positive semidefinite"

        # Check that it's Hermitian
        assert np.allclose(rho, rho.conj().T), "State should be Hermitian"

    def test_random_FF_state_pure(self):
        """Test random_FF_state with pure=True"""
        n_sites = 2

        psi = ff.random_FF_state(n_sites, pure=True, seed=42)

        # Check dimensions
        expected_dim = 2**n_sites
        assert psi.shape == (expected_dim, 1), f"Pure state should be {expected_dim}x1"

        # Check normalization
        assert np.allclose(np.linalg.norm(psi), 1.0), "Pure state should be normalized"

    def test_random_FF_state_returnH(self):
        """Test random_FF_state with returnH=True"""
        n_sites = 2

        # Test mixed state with returnH
        rho, H_op = ff.random_FF_state(n_sites, returnH=True, seed=42)

        # Check that both are returned
        expected_dim = 2**n_sites
        assert rho.shape == (expected_dim, expected_dim), "State should be correct size"
        assert H_op.shape == (
            expected_dim,
            expected_dim,
        ), "Hamiltonian should be correct size"

        # Check normalization
        assert np.allclose(np.trace(rho), 1.0), "State should be normalized"

        # Check that Hamiltonian is Hermitian
        assert np.allclose(H_op, H_op.conj().T), "Hamiltonian should be Hermitian"

    def test_random_FF_state_pure_returnH(self):
        """Test random_FF_state with pure=True and returnH=True"""
        n_sites = 2

        psi, H_op = ff.random_FF_state(n_sites, pure=True, returnH=True, seed=42)

        # Check dimensions
        expected_dim = 2**n_sites
        assert psi.shape == (expected_dim, 1), f"Pure state should be {expected_dim}x1"
        assert H_op.shape == (
            expected_dim,
            expected_dim,
        ), f"Hamiltonian should be {expected_dim}x{expected_dim}"

        # Check normalization
        assert np.allclose(np.linalg.norm(psi), 1.0), "Pure state should be normalized"

    def test_random_FF_state_fixedN(self):
        """Test random_FF_state with fixedN=True"""
        n_sites = 2

        rho = ff.random_FF_state(n_sites, fixedN=True, seed=42)

        # Check basic properties
        expected_dim = 2**n_sites
        assert rho.shape == (
            expected_dim,
            expected_dim,
        ), f"State should be {expected_dim}x{expected_dim}"
        assert np.allclose(np.trace(rho), 1.0), "State should be normalized"
        assert np.allclose(rho, rho.conj().T), "State should be Hermitian"

    def test_random_FF_state_reproducibility(self):
        """Test that random_FF_state is reproducible with seed"""
        n_sites = 2

        rho1 = ff.random_FF_state(n_sites, seed=123)
        rho2 = ff.random_FF_state(n_sites, seed=123)

        assert np.allclose(rho1, rho2), "Should be reproducible with same seed"

    def test_random_FF_state_different_seeds(self):
        """Test that different seeds produce different states"""
        n_sites = 2

        rho1 = ff.random_FF_state(n_sites, seed=123)
        rho2 = ff.random_FF_state(n_sites, seed=456)

        # States should be different (with high probability)
        assert not np.allclose(
            rho1, rho2, atol=1e-10
        ), "Different seeds should produce different states"
