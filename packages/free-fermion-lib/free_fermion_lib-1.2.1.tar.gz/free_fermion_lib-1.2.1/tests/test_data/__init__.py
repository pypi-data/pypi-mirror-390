"""
Test Data Package for Free Fermion Library

This package contains reference data, expected results, and test matrices
used throughout the test suite for validation and benchmarking.

Contents:
- Reference matrices with known properties
- Expected results for validation
- Benchmark data for performance testing
- Example systems for integration testing
"""

import numpy as np
import os

# Package metadata
__version__ = "1.0.0"
__author__ = "Free Fermion Library Team"

# Data directory path
DATA_DIR = os.path.dirname(os.path.abspath(__file__))


def load_test_matrix(name):
    """Load a test matrix by name"""
    filepath = os.path.join(DATA_DIR, f"{name}.npy")
    if os.path.exists(filepath):
        return np.load(filepath)
    else:
        raise FileNotFoundError(f"Test matrix '{name}' not found")


def save_test_matrix(matrix, name):
    """Save a test matrix with given name"""
    filepath = os.path.join(DATA_DIR, f"{name}.npy")
    np.save(filepath, matrix)


def list_test_matrices():
    """List available test matrices"""
    matrices = []
    for filename in os.listdir(DATA_DIR):
        if filename.endswith(".npy"):
            matrices.append(filename[:-4])  # Remove .npy extension
    return sorted(matrices)


# Common test matrices
def get_pauli_matrices():
    """Get the standard Pauli matrices"""
    sigma_x = np.array([[0, 1], [1, 0]], dtype=complex)
    sigma_y = np.array([[0, -1j], [1j, 0]], dtype=complex)
    sigma_z = np.array([[1, 0], [0, -1]], dtype=complex)
    sigma_0 = np.array([[1, 0], [0, 1]], dtype=complex)

    return {
        "sigma_x": sigma_x,
        "sigma_y": sigma_y,
        "sigma_z": sigma_z,
        "sigma_0": sigma_0,
    }


def get_test_correlation_matrices():
    """Get standard test correlation matrices"""
    # 2x2 correlation matrix
    gamma_2x2 = np.array([[0.5, 0.0], [0.0, 0.5]])

    # 4x4 correlation matrix for two-site system
    gamma_4x4 = np.array(
        [
            [0.5, 0.0, 0.2, 0.0],
            [0.0, 0.5, 0.0, 0.2],
            [0.2, 0.0, 0.5, 0.0],
            [0.0, 0.2, 0.0, 0.5],
        ]
    )

    return {"gamma_2x2": gamma_2x2, "gamma_4x4": gamma_4x4}


def get_test_hamiltonians():
    """Get standard test Hamiltonians"""
    # Simple 2-site hopping Hamiltonian
    H_2site = np.array([[-1.0, 1.0], [1.0, -1.0]])

    # 4-site chain Hamiltonian
    H_4site = np.array(
        [
            [0.0, -1.0, 0.0, 0.0],
            [-1.0, 0.0, -1.0, 0.0],
            [0.0, -1.0, 0.0, -1.0],
            [0.0, 0.0, -1.0, 0.0],
        ]
    )

    return {"H_2site": H_2site, "H_4site": H_4site}
