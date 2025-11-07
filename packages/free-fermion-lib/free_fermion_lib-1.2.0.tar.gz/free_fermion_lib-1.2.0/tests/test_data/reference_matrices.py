"""
Reference Matrices for Free Fermion Library Tests

This module contains reference matrices with known properties and expected results
for validation of the Free Fermion Library functions.
"""

import numpy as np

# Known pfaffian values
PFAFFIAN_TEST_CASES = {
    "pf_2x2_identity": {
        "matrix": np.array([[0, 1], [-1, 0]]),
        "pfaffian": 1.0,
        "description": "2x2 skew-symmetric identity-like matrix",
    },
    "pf_4x4_example": {
        "matrix": np.array(
            [[0, 1, 2, 3], [-1, 0, 4, 5], [-2, -4, 0, 6], [-3, -5, -6, 0]]
        ),
        "pfaffian": -20.0,  # Known result
        "description": "4x4 skew-symmetric test matrix",
    },
    "pf_4x4_simple": {
        "matrix": np.array(
            [[0, 2, 1, 0], [-2, 0, 0, 1], [-1, 0, 0, 2], [0, -1, -2, 0]]
        ),
        "pfaffian": 5.0,  # Known result
        "description": "4x4 simple skew-symmetric matrix",
    },
}

# Known hafnian values
HAFNIAN_TEST_CASES = {
    "hf_2x2_simple": {
        "matrix": np.array([[1, 2], [2, 3]]),
        "hafnian": 2.0,
        "description": "2x2 symmetric matrix",
    },
    "hf_4x4_ones": {
        "matrix": np.ones((4, 4)),
        "hafnian": 3.0,  # Known result for all-ones 4x4
        "description": "4x4 all-ones matrix",
    },
}

# Known permanent values
PERMANENT_TEST_CASES = {
    "pt_2x2_identity": {
        "matrix": np.eye(2),
        "permanent": 1.0,
        "description": "2x2 identity matrix",
    },
    "pt_3x3_ones": {
        "matrix": np.ones((3, 3)),
        "permanent": 6.0,  # 3! = 6
        "description": "3x3 all-ones matrix",
    },
    "pt_3x3_permutation": {
        "matrix": np.array([[0, 1, 0], [0, 0, 1], [1, 0, 0]]),
        "permanent": 1.0,
        "description": "3x3 permutation matrix",
    },
}

# Known determinant values
DETERMINANT_TEST_CASES = {
    "dt_2x2_simple": {
        "matrix": np.array([[2, 3], [4, 5]]),
        "determinant": -2.0,  # 2*5 - 3*4 = -2
        "description": "2x2 simple matrix",
    },
    "dt_3x3_triangular": {
        "matrix": np.array([[2, 3, 4], [0, 5, 6], [0, 0, 7]]),
        "determinant": 70.0,  # 2*5*7 = 70
        "description": "3x3 upper triangular matrix",
    },
}

# Perfect matching test cases
PERFECT_MATCHING_TEST_CASES = {
    "pm_path_4": {
        "adjacency_matrix": np.array(
            [[0, 1, 0, 0], [1, 0, 1, 0], [0, 1, 0, 1], [0, 0, 1, 0]]
        ),
        "perfect_matchings": 1,
        "description": "Path graph with 4 vertices",
    },
    "pm_cycle_4": {
        "adjacency_matrix": np.array(
            [[0, 1, 0, 1], [1, 0, 1, 0], [0, 1, 0, 1], [1, 0, 1, 0]]
        ),
        "perfect_matchings": 2,
        "description": "4-cycle graph",
    },
    "pm_complete_4": {
        "adjacency_matrix": np.array(
            [[0, 1, 1, 1], [1, 0, 1, 1], [1, 1, 0, 1], [1, 1, 1, 0]]
        ),
        "perfect_matchings": 3,
        "description": "Complete graph K4",
    },
}

# Correlation matrix test cases
CORRELATION_MATRIX_TEST_CASES = {
    "corr_2site_half_filled": {
        "hamiltonian": np.array([[0, -1], [-1, 0]]),
        "correlation_matrix": np.array([[0.5, 0.5], [0.5, 0.5]]),
        "description": "2-site half-filled system",
    },
    "corr_2site_empty": {
        "hamiltonian": np.array([[1, -1], [-1, 1]]),
        "correlation_matrix": np.array([[0, 0], [0, 0]]),
        "description": "2-site empty system",
    },
}

# Symplectic test cases
SYMPLECTIC_TEST_CASES = {
    "symp_2x2_simple": {
        "matrix": np.array([[0, 1], [-1, 0]]),
        "eigenvalues": np.array([1j, -1j]),
        "description": "2x2 symplectic matrix",
    }
}

# Kitaev chain test cases
KITAEV_CHAIN_TEST_CASES = {
    "kitaev_trivial": {
        "length": 4,
        "hopping": 1.0,
        "chemical_potential": 2.0,
        "pairing": 0.5,
        "topological": False,
        "description": "Trivial phase Kitaev chain",
    },
    "kitaev_topological": {
        "length": 4,
        "hopping": 1.0,
        "chemical_potential": 0.0,
        "pairing": 0.5,
        "topological": True,
        "description": "Topological phase Kitaev chain",
    },
}

# Gaussian state test cases
GAUSSIAN_STATE_TEST_CASES = {
    "vacuum_state": {
        "covariance_matrix": np.eye(4),
        "description": "Vacuum Gaussian state",
    },
    "thermal_state": {"temperature": 1.0, "description": "Thermal Gaussian state"},
}


def get_all_test_cases():
    """Get all test cases organized by category"""
    return {
        "pfaffian": PFAFFIAN_TEST_CASES,
        "hafnian": HAFNIAN_TEST_CASES,
        "permanent": PERMANENT_TEST_CASES,
        "determinant": DETERMINANT_TEST_CASES,
        "perfect_matching": PERFECT_MATCHING_TEST_CASES,
        "correlation_matrix": CORRELATION_MATRIX_TEST_CASES,
        "symplectic": SYMPLECTIC_TEST_CASES,
        "kitaev_chain": KITAEV_CHAIN_TEST_CASES,
        "gaussian_state": GAUSSIAN_STATE_TEST_CASES,
    }


def validate_test_case(category, name, result, tolerance=1e-10):
    """Validate a computed result against reference data"""
    all_cases = get_all_test_cases()

    if category not in all_cases:
        raise ValueError(f"Unknown test category: {category}")

    if name not in all_cases[category]:
        raise ValueError(f"Unknown test case: {name} in category {category}")

    test_case = all_cases[category][name]

    # Determine the expected value based on category
    if category == "pfaffian":
        expected = test_case["pfaffian"]
    elif category == "hafnian":
        expected = test_case["hafnian"]
    elif category == "permanent":
        expected = test_case["permanent"]
    elif category == "determinant":
        expected = test_case["determinant"]
    elif category == "perfect_matching":
        expected = test_case["perfect_matchings"]
    else:
        raise ValueError(f"Validation not implemented for category: {category}")

    # Check if result matches expected value
    if isinstance(expected, np.ndarray):
        return np.allclose(result, expected, atol=tolerance)
    else:
        return abs(result - expected) < tolerance


def get_benchmark_matrices():
    """Get matrices for performance benchmarking"""
    sizes = [10, 20, 50, 100]
    matrices = {}

    for n in sizes:
        # Random symmetric matrix
        A_sym = np.random.randn(n, n)
        A_sym = A_sym + A_sym.T
        matrices[f"symmetric_{n}x{n}"] = A_sym

        # Random skew-symmetric matrix
        A_skew = np.random.randn(n, n)
        A_skew = A_skew - A_skew.T
        matrices[f"skew_symmetric_{n}x{n}"] = A_skew

        # Random Hermitian matrix
        A_herm = np.random.randn(n, n) + 1j * np.random.randn(n, n)
        A_herm = A_herm + A_herm.T.conj()
        matrices[f"hermitian_{n}x{n}"] = A_herm

    return matrices
