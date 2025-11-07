"""
Combinatorics Tests for Free Fermion Library

This module contains comprehensive tests for the combinatorial functions in
ff_combinatorics.py, including pfaffians, hafnians, permanents, determinants,
and their mathematical properties.

Test categories:
- Pfaffian calculations and properties
- Hafnian calculations and properties
- Permanent and determinant calculations
- Mathematical relationships and edge cases
- Sign function testing
"""

import math

import numpy as np
import pytest

# Import the library
import ff


class TestPfaffianFunction:
    """Test pfaffian calculation and properties"""

    def test_pfaffian_known_matrices(self):
        """Test pfaffian with matrices having known results"""
        # 2x2 case: pf([[0,1],[-1,0]]) = 1
        A2 = np.array([[0, 1], [-1, 0]])
        pf_val = ff.pf(A2)
        assert np.allclose(pf_val, 1), "pf([[0,1],[-1,0]]) should be 1"

        # 4x4 case from documentation
        A4 = np.array([[0, 1, 2, 3], [-1, 0, 4, 5], [-2, -4, 0, 6], [-3, -5, -6, 0]])
        pf_val = ff.pf(A4)
        det_val = np.linalg.det(A4)
        assert np.allclose(pf_val**2, det_val), "pf(A)^2 should equal det(A)"

        # Another 4x4 example
        B4 = np.array([[0, 2, 1, 0], [-2, 0, 0, 1], [-1, 0, 0, 2], [0, -1, -2, 0]])
        pf_val_b = ff.pf(B4)
        det_val_b = np.linalg.det(B4)
        assert np.allclose(pf_val_b**2, det_val_b), "pf(B)^2 should equal det(B)"

    def test_pfaffian_properties(self):
        """Test mathematical properties of pfaffian"""
        # Odd dimension should give 0
        A_odd = np.random.randn(3, 3)
        assert ff.pf(A_odd) == 0, "Pfaffian of odd-dimensional matrix should be 0"

        # Empty matrix should give 1
        A_empty = np.array([]).reshape(0, 0)
        assert ff.pf(A_empty) == 1, "Pfaffian of empty matrix should be 1"

        # Zero matrix should give 0
        A_zero = np.zeros((4, 4))
        assert ff.pf(A_zero) == 0, "Pfaffian of zero matrix should be 0"

        # Skew-symmetric property: pf(A)^2 = det(A) for skew-symmetric A
        n = 4
        A_random = np.random.randn(n, n)
        A_skew = A_random - A_random.T  # Make skew-symmetric

        pf_val = ff.pf(A_skew)
        det_val = np.linalg.det(A_skew)
        assert np.allclose(pf_val**2, det_val), "pf(A)^2 = det(A) for skew-symmetric A"

    def test_pfaffian_scaling(self):
        """Test pfaffian scaling properties"""
        A = np.array([[0, 1, 2, 3], [-1, 0, 4, 5], [-2, -4, 0, 6], [-3, -5, -6, 0]])

        # pf(cA) = c^(n/2) pf(A) for n×n matrix
        c = 2.0
        n = A.shape[0]

        pf_A = ff.pf(A)
        pf_cA = ff.pf(c * A)

        expected = c ** (n // 2) * pf_A
        assert np.allclose(pf_cA, expected), "pf(cA) should equal c^(n/2) pf(A)"

    def test_pfaffian_antisymmetry(self):
        """Test pfaffian antisymmetry under row/column swaps"""
        A = np.array([[0, 1, 2, 3], [-1, 0, 4, 5], [-2, -4, 0, 6], [-3, -5, -6, 0]])

        # Swap rows 0,1 and columns 0,1
        A_swapped = A.copy()
        A_swapped[[0, 1]] = A_swapped[[1, 0]]  # Swap rows
        A_swapped[:, [0, 1]] = A_swapped[:, [1, 0]]  # Swap columns

        pf_A = ff.pf(A)
        pf_A_swapped = ff.pf(A_swapped)

        # Should change sign
        assert np.allclose(
            pf_A_swapped, -pf_A
        ), "Pfaffian should change sign under row/col swap"

    def test_pfaffian_large_matrix(self):
        """Test pfaffian on larger matrices"""
        # 6x6 skew-symmetric matrix
        n = 6
        A_random = np.random.randn(n, n)
        A = A_random - A_random.T

        pf_val = ff.pf(A)
        det_val = np.linalg.det(A)

        assert np.allclose(pf_val**2, det_val), "pf(A)^2 = det(A) for 6x6 matrix"


class TestHafnianFunction:
    """Test hafnian calculation and properties"""

    def test_hafnian_known_matrices(self):
        """Test hafnian with matrices having known results"""
        # 2x2 case
        A2 = np.array([[1, 2], [2, 3]])
        hf_val = ff.hf(A2)
        # For 2x2 matrix [[a,b],[b,c]], hafnian = b
        assert np.allclose(hf_val, 2), "hf([[1,2],[2,3]]) should be 2"

        # 4x4 symmetric matrix
        A4 = np.array([[0, 1, 2, 3], [1, 0, 4, 5], [2, 4, 0, 6], [3, 5, 6, 0]])
        hf_val = ff.hf(A4)

        # Hafnian should be real and finite
        assert np.isfinite(hf_val), "Hafnian should be finite"
        assert np.allclose(hf_val.imag, 0), "Hafnian of real matrix should be real"

    def test_hafnian_properties(self):
        """Test mathematical properties of hafnian"""
        # Odd dimension should give 0
        A_odd = np.random.randn(3, 3)
        assert ff.hf(A_odd) == 0, "Hafnian of odd-dimensional matrix should be 0"

        # Empty matrix should give 1
        A_empty = np.array([]).reshape(0, 0)
        assert ff.hf(A_empty) == 1, "Hafnian of empty matrix should be 1"

        # Diagonal matrix: hafnian should be 0 (no off-diagonal perfect matching)
        A_diag = np.diag([1, 2, 3, 4])
        assert ff.hf(A_diag) == 0, "Hafnian of diagonal matrix should be 0"

    def test_hafnian_vs_permanent(self):
        """Test relationship between hafnian and permanent for special matrices"""
        # For a matrix with all 1s, hafnian and permanent have known relationship
        A = np.ones((4, 4))
        hf_val = ff.hf(A)
        pt_val = ff.pt(A)

        # Both should be positive for all-ones matrix
        assert hf_val > 0, "Hafnian of all-ones matrix should be positive"
        assert pt_val > 0, "Permanent of all-ones matrix should be positive"


class TestPermanentFunction:
    """Test permanent calculation and properties"""

    def test_permanent_known_matrices(self):
        """Test permanent with matrices having known results"""
        # Identity matrix: permanent = 1
        Id = np.eye(3)
        pt_val = ff.pt(Id)
        assert np.allclose(pt_val, 1), "Permanent of identity should be 1"

        # All-ones matrix: permanent = n!
        n = 3
        A_ones = np.ones((n, n))
        pt_val = ff.pt(A_ones)
        expected = math.factorial(n)
        assert np.allclose(
            pt_val, expected
        ), f"Permanent of {n}x{n} all-ones should be {n}!"

        # Permutation matrix: permanent = 1
        P = np.array([[0, 1, 0], [0, 0, 1], [1, 0, 0]])
        pt_val = ff.pt(P)
        assert np.allclose(pt_val, 1), "Permanent of permutation matrix should be 1"

    def test_permanent_properties(self):
        """Test mathematical properties of permanent"""
        # Zero matrix: permanent = 0
        A_zero = np.zeros((3, 3))
        assert ff.pt(A_zero) == 0, "Permanent of zero matrix should be 0"

        # Matrix with zero row: permanent = 0
        A_zero_row = np.array([[1, 2, 3], [0, 0, 0], [4, 5, 6]])
        assert ff.pt(A_zero_row) == 0, "Permanent with zero row should be 0"

        # Matrix with zero column: permanent = 0
        A_zero_col = np.array([[1, 0, 3], [2, 0, 5], [4, 0, 6]])
        assert ff.pt(A_zero_col) == 0, "Permanent with zero column should be 0"

    def test_permanent_vs_determinant(self):
        """Test relationship between permanent and determinant"""
        # For positive matrices, permanent ≥ |determinant|
        A_pos = np.array([[1, 2], [3, 4]])
        pt_val = ff.pt(A_pos)
        dt_val = ff.dt(A_pos)

        assert pt_val >= abs(
            dt_val
        ), "Permanent should be ≥ |determinant| for positive matrix"

        # For diagonal matrices, permanent = determinant
        A_diag = np.diag([2, 3, 4])
        pt_val = ff.pt(A_diag)
        dt_val = ff.dt(A_diag)

        assert np.allclose(
            pt_val, dt_val
        ), "Permanent = determinant for diagonal matrix"


class TestDeterminantFunction:
    """Test determinant calculation and properties"""

    def test_determinant_known_matrices(self):
        """Test determinant with matrices having known results"""
        # Identity matrix: det = 1
        Id = np.eye(3)
        dt_val = ff.dt(Id)
        assert np.allclose(dt_val, 1), "Determinant of identity should be 1"

        # 2x2 matrix: det = ad - bc
        A = np.array([[2, 3], [4, 5]])
        dt_val = ff.dt(A)
        expected = 2 * 5 - 3 * 4
        assert np.allclose(dt_val, expected), "det([[2,3],[4,5]]) should be 2*5-3*4"

        # Upper triangular: det = product of diagonal
        A_tri = np.array([[2, 3, 4], [0, 5, 6], [0, 0, 7]])
        dt_val = ff.dt(A_tri)
        expected = 2 * 5 * 7
        assert np.allclose(dt_val, expected), "det of triangular = product of diagonal"

    def test_determinant_vs_numpy(self):
        """Test that our determinant matches NumPy's"""
        A = np.random.randn(4, 4)

        dt_ours = ff.dt(A)
        dt_numpy = np.linalg.det(A)

        assert np.allclose(dt_ours, dt_numpy), "Our determinant should match NumPy's"

    def test_determinant_properties(self):
        """Test mathematical properties of determinant"""
        # Zero matrix: det = 0
        A_zero = np.zeros((3, 3))
        assert ff.dt(A_zero) == 0, "Determinant of zero matrix should be 0"

        # Singular matrix: det = 0
        A_singular = np.array([[1, 2, 3], [2, 4, 6], [1, 1, 1]])
        dt_val = ff.dt(A_singular)
        assert np.allclose(dt_val, 0), "Determinant of singular matrix should be 0"

        # Scaling: det(cA) = c^n det(A)
        A = np.random.randn(3, 3)
        c = 2.0
        n = A.shape[0]

        dt_A = ff.dt(A)
        dt_cA = ff.dt(c * A)

        expected = c**n * dt_A
        assert np.allclose(dt_cA, expected), "det(cA) should equal c^n det(A)"


class TestDeterminantEigenFunction:
    """Test eigenvalue-based determinant calculation"""

    def test_dt_eigen_vs_regular(self):
        """Test that eigenvalue determinant matches regular determinant"""
        A = np.random.randn(4, 4)

        dt_regular = ff.dt(A)
        dt_eigen = ff.dt_eigen(A)

        assert np.allclose(
            dt_regular, dt_eigen
        ), "Eigenvalue determinant should match regular determinant"

    def test_dt_eigen_properties(self):
        """Test properties of eigenvalue-based determinant"""
        # Hermitian matrix
        A = np.random.randn(3, 3)
        A_herm = A + A.T

        dt_val = ff.dt_eigen(A_herm)
        assert np.isfinite(dt_val), "Determinant should be finite"

        # For real symmetric matrix, determinant should be real
        assert np.allclose(dt_val.imag, 0), "Determinant of real matrix should be real"

    def test_dt_eigen_edge_cases(self):
        """Test edge cases for eigenvalue determinant"""
        # Non-square matrix should return None
        A_nonsquare = np.random.randn(3, 4)
        result = ff.dt_eigen(A_nonsquare)
        assert result is None, "Non-square matrix should return None"

        # Identity matrix
        Id = np.eye(4)
        dt_val = ff.dt_eigen(Id)
        assert np.allclose(dt_val, 1), "det(I) should be 1"


class TestSignFunction:
    """Test sign function for permutations"""

    def test_sign_known_permutations(self):
        """Test sign function with known permutations"""
        # Identity permutation: sign = +1
        identity = [0, 1, 2]
        assert ff.sgn(identity) == 1, "Identity permutation should have sign +1"

        # Single transposition: sign = -1
        transposition = [1, 0, 2]
        assert ff.sgn(transposition) == -1, "Single transposition should have sign -1"

        # Cycle of length 3: sign = +1 (even number of transpositions)
        cycle3 = [1, 2, 0]
        assert ff.sgn(cycle3) == 1, "3-cycle should have sign +1"

        # Two transpositions: sign = +1
        two_trans = [1, 0, 3, 2]
        assert ff.sgn(two_trans) == 1, "Two transpositions should have sign +1"

    def test_sign_properties(self):
        """Test mathematical properties of sign function"""
        # Sign of inverse permutation
        perm = [2, 0, 1]
        inv_perm = [1, 2, 0]  # Inverse of [2, 0, 1]

        assert ff.sgn(perm) == ff.sgn(
            inv_perm
        ), "Permutation and inverse should have same sign"

        # Composition of permutations
        perm1 = [1, 0, 2]  # sign = -1
        perm2 = [0, 2, 1]  # sign = -1

        # Compose: apply perm1 then perm2
        composed = [perm2[perm1[i]] for i in range(len(perm1))]

        sign1 = ff.sgn(perm1)
        sign2 = ff.sgn(perm2)
        sign_composed = ff.sgn(composed)

        assert sign_composed == sign1 * sign2, "sgn(σ∘τ) = sgn(σ)sgn(τ)"

    def test_sign_inversion_count(self):
        """Test that sign equals (-1)^(number of inversions)"""

        def count_inversions(perm):
            """Count inversions in permutation"""
            count = 0
            for i in range(len(perm)):
                for j in range(i + 1, len(perm)):
                    if perm[i] > perm[j]:
                        count += 1
            return count

        # Test several permutations
        perms = [[0, 1, 2], [1, 0, 2], [2, 1, 0], [1, 2, 0]]

        for perm in perms:
            inversions = count_inversions(perm)
            expected_sign = (-1) ** inversions
            actual_sign = ff.sgn(perm)

            assert (
                actual_sign == expected_sign
            ), f"Sign of {perm} should be (-1)^{inversions} = {expected_sign}"


class TestCombinatoricsEdgeCases:
    """Test edge cases and error conditions"""

    def test_empty_inputs(self):
        """Test behavior with empty inputs"""
        empty = np.array([]).reshape(0, 0)

        # Empty matrix results
        assert ff.pf(empty) == 1, "pf of empty matrix should be 1"
        assert ff.hf(empty) == 1, "hf of empty matrix should be 1"
        assert ff.pt(empty) == 1, "pt of empty matrix should be 1"
        assert ff.dt(empty) == 1, "dt of empty matrix should be 1"

    def test_single_element(self):
        """Test behavior with 1x1 matrices"""
        A = np.array([[5]])

        # 1x1 matrix results (odd dimension for pf/hf)
        assert ff.pf(A) == 0, "pf of 1x1 matrix should be 0"
        assert ff.hf(A) == 0, "hf of 1x1 matrix should be 0"
        assert ff.pt(A) == 5, "pt of [[5]] should be 5"
        assert ff.dt(A) == 5, "dt of [[5]] should be 5"

    def test_complex_matrices(self):
        """Test behavior with complex matrices"""
        A = np.array([[1 + 1j, 2 - 1j], [2 + 1j, 3 - 1j]])

        # All functions should handle complex input
        pf_val = ff.pf(A)
        hf_val = ff.hf(A)
        pt_val = ff.pt(A)
        dt_val = ff.dt(A)

        # Results should be finite complex numbers
        for val in [pf_val, hf_val, pt_val, dt_val]:
            assert np.isfinite(val), "Result should be finite"

    def test_very_small_matrices(self):
        """Test with very small numerical values"""
        A = 1e-10 * np.array([[0, 1], [-1, 0]])

        pf_val = ff.pf(A)
        expected = 1e-10  # pf scales linearly for 2x2

        assert np.allclose(pf_val, expected), "Should handle small values correctly"

    def test_large_matrices_performance(self):
        """Test that functions don't crash on moderately large matrices"""
        # Note: These are computationally expensive, so we use small "large" matrices
        n = 6
        A = np.random.randn(n, n)
        A_skew = A - A.T

        # Should complete without error (though may be slow)
        try:
            pf_val = ff.pf(A_skew)
            assert np.isfinite(pf_val), "Pfaffian should be finite"
        except Exception as e:
            pytest.fail(f"Pfaffian calculation failed on {n}x{n} matrix: {e}")


class TestMathematicalRelationships:
    """Test mathematical relationships between different functions"""

    def test_pfaffian_determinant_relationship(self):
        """Test pf(A)^2 = det(A) for skew-symmetric matrices"""
        sizes = [2, 4, 6]

        for n in sizes:
            # Create random skew-symmetric matrix
            A_random = np.random.randn(n, n)
            A = A_random - A_random.T

            pf_val = ff.pf(A)
            det_val = ff.dt(A)

            assert np.allclose(
                pf_val**2, det_val
            ), f"pf(A)^2 should equal det(A) for {n}x{n} skew-symmetric matrix"

    def test_determinant_consistency(self):
        """Test that different determinant methods give same result"""
        A = np.random.randn(4, 4)

        dt_combinatorial = ff.dt(A)
        dt_eigenvalue = ff.dt_eigen(A)
        dt_numpy = np.linalg.det(A)

        assert np.allclose(
            dt_combinatorial, dt_numpy
        ), "Combinatorial determinant should match NumPy"
        assert np.allclose(
            dt_eigenvalue, dt_numpy
        ), "Eigenvalue determinant should match NumPy"
        assert np.allclose(
            dt_combinatorial, dt_eigenvalue
        ), "Both determinant methods should agree"

    def test_permanent_hafnian_relationship(self):
        """Test relationships between permanent and hafnian for special cases"""
        # For diagonal matrices: permanent = product of diagonal, hafnian = 0
        A_diag = np.diag([2, 3, 4, 5])

        pt_val = ff.pt(A_diag)
        hf_val = ff.hf(A_diag)

        expected_pt = 2 * 3 * 4 * 5
        assert np.allclose(
            pt_val, expected_pt
        ), "Permanent of diagonal should be product"
        assert np.allclose(hf_val, 0), "Hafnian of diagonal should be 0"
