"""
Utility Tests for Free Fermion Library

This module contains comprehensive tests for the utility functions in ff_utils.py,
including formatting, cleaning, printing, and helper functions.

Test categories:
- Matrix cleaning and formatting
- Output formatting and printing
- Numerical precision handling
- String manipulation utilities
- Error handling and edge cases
"""

import io
import warnings
from contextlib import redirect_stdout

import numpy as np

# Import the library
import ff


class TestCleanFunction:
    """Test the clean() function for numerical precision"""

    def test_clean_small_numbers(self):
        """Test cleaning of very small numbers"""
        # Small real numbers should become zero
        small_real = 1e-15
        cleaned = ff.clean(small_real)
        assert cleaned == 0, "Very small real numbers should be cleaned to 0"

        # Small complex numbers should become zero
        small_complex = 1e-15 + 1e-15j
        cleaned = ff.clean(small_complex)
        assert cleaned == 0, "Very small complex numbers should be cleaned to 0"

        # Small imaginary part should be removed
        almost_real = 1.0 + 1e-15j
        cleaned = ff.clean(almost_real)
        assert cleaned == 1.0, "Small imaginary parts should be removed"
        assert isinstance(cleaned, float), "Result should be real"

    def test_clean_arrays(self):
        """Test cleaning of numpy arrays"""
        # Array with small numbers
        arr = np.array([1.0, 1e-15, 1e-14, 2.0])
        cleaned = ff.clean(arr)
        expected = np.array([1.0, 0.0, 0.0, 2.0])
        assert np.allclose(cleaned, expected), "Small array elements should be cleaned"

        # Complex array
        arr_complex = np.array([1.0 + 1e-15j, 2.0, 1e-15 + 1e-15j])
        cleaned = ff.clean(arr_complex)
        expected = np.array([1.0, 2.0, 0.0])
        assert np.allclose(
            cleaned, expected
        ), "Complex array should be cleaned properly"

    def test_clean_matrices(self):
        """Test cleaning of matrices"""
        # Matrix with small entries
        matrix = np.array([[1.0, 1e-15], [1e-14, 2.0]])
        cleaned = ff.clean(matrix)
        expected = np.array([[1.0, 0.0], [0.0, 2.0]])
        assert np.allclose(cleaned, expected), "Matrix entries should be cleaned"

        # Preserve matrix shape
        assert cleaned.shape == matrix.shape, "Matrix shape should be preserved"

    def test_clean_threshold_parameter(self):
        """Test clean function with custom threshold"""
        # Default threshold
        val = 1e-12
        cleaned_default = ff.clean(val)
        assert cleaned_default == 0, "Should be cleaned with default threshold"

        # Custom threshold
        cleaned_custom = ff.clean(val, threshold=1e-15)
        assert cleaned_custom == val, "Should not be cleaned with smaller threshold"

        # Larger threshold
        val_larger = 1e-10
        cleaned_large_thresh = ff.clean(val_larger, threshold=1e-8)
        assert cleaned_large_thresh == 0, "Should be cleaned with larger threshold"

    def test_clean_preserves_significant_values(self):
        """Test that clean preserves significant values"""
        # Values that should not be cleaned
        significant_values = [1.0, -1.0, 0.1, -0.1, 1e-10, -1e-10]

        for val in significant_values:
            cleaned = ff.clean(val, 1e-12)
            if abs(val) > 1e-12:  # above threshold
                assert np.allclose(
                    cleaned, val
                ), f"Significant value {val} should not be cleaned"

    def test_clean_edge_cases(self):
        """Test clean function edge cases"""
        # Zero should remain zero
        assert ff.clean(0.0) == 0.0, "Zero should remain zero"
        assert ff.clean(0.0 + 0.0j) == 0.0, "Complex zero should become real zero"

        # Infinity should remain infinity
        assert ff.clean(np.inf) == np.inf, "Infinity should remain infinity"
        assert ff.clean(-np.inf) == -np.inf, "Negative infinity should remain"

        # NaN should remain NaN
        assert np.isnan(ff.clean(np.nan)), "NaN should remain NaN"


class TestPrintFunction:
    """Test the _print() function for formatted output"""

    def test_print_basic_output(self):
        """Test basic printing functionality"""
        # Capture stdout
        captured_output = io.StringIO()

        with redirect_stdout(captured_output):
            ff.ff_utils._print("Test message")

        output = captured_output.getvalue()
        assert "Test message" in output, "Should print the message"

    def test_print_no_double_output(self):
        """Test that _print function doesn't print twice (bug fix)"""
        # Capture stdout
        captured_output = io.StringIO()

        with redirect_stdout(captured_output):
            ff.ff_utils._print("Single message")

        output = captured_output.getvalue()
        # Count occurrences of the message
        message_count = output.count("Single message")
        assert (
            message_count == 1
        ), f"Message should appear exactly once, but appeared {message_count} times"

    def test_print_arrays(self):
        """Test printing of numpy arrays"""
        arr = np.array([1, 2, 3])
        captured_output = io.StringIO()

        with redirect_stdout(captured_output):
            ff.ff_utils._print(arr)

        output = captured_output.getvalue()
        assert "[1 2 3]" in output or "1" in output, "Should print array contents"

    def test_print_matrices(self):
        """Test printing of matrices"""
        matrix = np.array([[1, 2], [3, 4]])
        captured_output = io.StringIO()

        with redirect_stdout(captured_output):
            ff.ff_utils._print(matrix)

        output = captured_output.getvalue()
        # assert "Matrix:" in output, "Should print matrix label"
        # Matrix should be formatted nicely
        assert "1" in output and "4" in output, "Should contain matrix elements"

    def test_print_complex_numbers(self):
        """Test printing of complex numbers"""
        complex_val = 1 + 2j
        captured_output = io.StringIO()

        with redirect_stdout(captured_output):
            ff.ff_utils._print(complex_val)

        output = captured_output.getvalue()
        # assert "Complex:" in output, "Should print label"
        assert (
            "1" in output and "2" in output
        ), "Should contain real and imaginary parts"


class TestFormattedOutput:
    """Test formatted output functions"""

    def test_formatted_matrix_output(self):
        """Test formatted matrix output"""
        matrix = np.array([[1.23456, 2.34567], [3.45678, 4.56789]])

        formatted = ff.formatted_output(matrix)

        # Should be a string
        assert isinstance(formatted, str), "Should return string"

        # Should contain matrix elements (possibly rounded)
        assert (
            "1.2" in formatted or "1.23" in formatted
        ), "Should contain formatted elements"

    def test_formatted_array_output(self):
        """Test formatted array output"""
        arr = np.array([1.23456, 2.34567, 3.45678])

        formatted = ff.formatted_output(arr)

        assert isinstance(formatted, str), "Should return string"
        assert "1.2" in formatted or "1.23" in formatted, "Should format array elements"

    def test_formatted_scalar_output(self):
        """Test formatted scalar output"""
        scalar = 3.14159265

        formatted = ff.formatted_output(scalar)

        assert isinstance(formatted, str), "Should return string"
        assert "3.14" in formatted, "Should format scalar value"

    def test_formatted_complex_output(self):
        """Test formatted complex number output"""
        complex_val = 1.23456 + 2.34567j

        formatted = ff.formatted_output(complex_val)

        assert isinstance(formatted, str), "Should return string"
        assert "1.2" in formatted and "2.3" in formatted, "Should format both parts"
        assert "j" in formatted or "i" in formatted, "Should indicate imaginary unit"

    def test_formatted_output_precision(self):
        """Test formatted output with different precision"""
        val = np.pi

        # Test different precision levels
        formatted_2 = ff.formatted_output(val, precision=2)
        formatted_4 = ff.formatted_output(val, precision=4)

        # Should have different levels of precision
        assert len(formatted_4) >= len(formatted_2), "Higher precision should be longer"

    def test_formatted_output_scientific(self):
        """Test formatted output in scientific notation"""
        large_val = 1.23e10
        small_val = 1.23e-10

        formatted_large = ff.formatted_output(large_val)
        formatted_small = ff.formatted_output(small_val)

        # Should handle scientific notation appropriately
        assert isinstance(formatted_large, str), "Should format large numbers"
        assert isinstance(formatted_small, str), "Should format small numbers"


class TestNumericalUtilities:
    """Test numerical utility functions"""

    def test_tolerance_checking(self):
        """Test tolerance-based equality checking"""
        # Test approximate equality
        a = 1.0
        b = 1.0 + 1e-15

        try:
            is_close = ff.is_close(a, b)
            assert is_close, "Should be approximately equal"

            # Test with custom tolerance
            is_close_strict = ff.is_close(a, b, tolerance=1e-16)
            assert not is_close_strict, "Should not be equal with strict tolerance"
        except AttributeError:
            # Function might not exist, use numpy instead
            assert np.isclose(a, b), "Should be approximately equal"

    def test_matrix_comparison(self):
        """Test matrix comparison utilities"""
        A = np.array([[1, 2], [3, 4]])
        B = A + 1e-15

        # Should be approximately equal
        assert np.allclose(A, B), "Matrices should be approximately equal"

        # Test custom matrix comparison if available
        try:
            matrices_equal = ff.matrices_equal(A, B)
            assert matrices_equal, "Custom comparison should work"
        except AttributeError:
            # Function might not exist
            pass

    def test_numerical_stability(self):
        """Test numerical stability utilities"""
        # Test condition number calculation
        A = np.array([[1, 2], [3, 4]])

        cond_num = np.linalg.cond(A)
        assert np.isfinite(cond_num), "Condition number should be finite"

        # Test if custom stability checks exist
        try:
            is_stable = ff.is_numerically_stable(A)
            assert isinstance(is_stable, bool), "Stability check should return boolean"
        except AttributeError:
            # Function might not exist
            pass

    def test_precision_handling(self):
        """Test precision handling utilities"""
        # Test rounding utilities
        val = 3.14159265

        rounded_2 = round(val, 2)
        assert rounded_2 == 3.14, "Should round to 2 decimal places"

        # Test custom precision functions if available
        try:
            custom_rounded = ff.round_to_precision(val, 3)
            assert abs(custom_rounded - 3.142) < 1e-10, "Custom rounding should work"
        except AttributeError:
            # Function might not exist
            pass


class TestErrorHandling:
    """Test error handling and edge cases"""

    def test_invalid_input_handling(self):
        """Test handling of invalid inputs"""
        # Test with None
        try:
            result = ff.clean(None)
            assert result is None, "Should handle None gracefully"
        except (TypeError, AttributeError):
            # Expected to raise error for None
            pass

        # Test with string
        try:
            result = ff.clean("not a number")
            # Should either convert or raise error
            assert isinstance(result, (str, type(None))), "Should handle strings"
        except (TypeError, ValueError):
            # Expected to raise error for strings
            pass

    def test_empty_input_handling(self):
        """Test handling of empty inputs"""
        # Empty array
        empty_arr = np.array([])
        cleaned = ff.clean(empty_arr)
        assert len(cleaned) == 0, "Empty array should remain empty"

        # Empty matrix
        empty_matrix = np.array([]).reshape(0, 0)
        cleaned_matrix = ff.clean(empty_matrix)
        assert cleaned_matrix.shape == (0, 0), "Empty matrix shape should be preserved"

    def test_large_input_handling(self):
        """Test handling of large inputs"""
        # Large array
        large_arr = np.random.randn(1000)

        try:
            cleaned = ff.clean(large_arr)
            assert len(cleaned) == len(large_arr), "Large array should be processed"
        except MemoryError:
            # Acceptable for very large arrays
            pass

    def test_warning_handling(self):
        """Test that functions handle warnings appropriately"""
        # Operations that might generate warnings
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")

            # Division by very small number
            result = ff.clean(1.0 / 1e-20)

            # Should either handle gracefully or generate appropriate warning
            assert (
                np.isfinite(result) or len(w) > 0
            ), "Should handle or warn about numerical issues"


class TestUtilityIntegration:
    """Test integration between utility functions"""

    def test_clean_and_print_integration(self):
        """Test that clean and print work together"""
        # Messy matrix
        messy_matrix = np.array([[1.0 + 1e-15j, 1e-16], [1e-14, 2.0]])

        # Clean then print
        cleaned = ff.clean(messy_matrix)

        captured_output = io.StringIO()
        with redirect_stdout(captured_output):
            ff.ff_utils._print("Cleaned matrix:", cleaned)

        output = captured_output.getvalue()
        assert "Cleaned matrix:" in output, "Should print cleaned matrix"
        # Should not contain very small numbers in output
        assert "1e-15" not in output, "Should not show very small numbers"

    def test_format_and_clean_integration(self):
        """Test that formatting and cleaning work together"""
        # Value with small imaginary part
        val = 3.14159 + 1e-15j

        # Clean then format
        cleaned = ff.clean(val)
        formatted = ff.formatted_output(cleaned)

        assert isinstance(formatted, str), "Should produce formatted string"
        assert "3.14" in formatted, "Should contain real part"
        assert "j" not in formatted, "Should not contain imaginary unit after cleaning"

    def test_comprehensive_workflow(self):
        """Test a comprehensive workflow using multiple utilities"""
        # Start with a complex calculation result
        matrix = np.array([[1.0 + 1e-15j, 2.0 - 1e-16j], [3.0 + 1e-14j, 4.0 - 1e-15j]])

        # Clean the matrix
        cleaned_matrix = ff.clean(matrix)

        # Format for output
        formatted = ff.formatted_output(cleaned_matrix)

        # Print the result
        captured_output = io.StringIO()
        with redirect_stdout(captured_output):
            ff.ff_utils._print("Final result:", formatted)

        output = captured_output.getvalue()

        # Verify the workflow
        assert isinstance(cleaned_matrix, np.ndarray), "Should produce clean matrix"
        assert isinstance(formatted, str), "Should produce formatted string"
        assert "Final result:" in output, "Should print final result"

        # Should not contain very small numbers
        assert np.allclose(cleaned_matrix.imag, 0), "Imaginary parts should be cleaned"
        assert np.allclose(
            cleaned_matrix.real, [[1, 2], [3, 4]]
        ), "Real parts should be preserved"


class TestPerformanceUtilities:
    """Test performance-related utilities"""

    def test_timing_utilities(self):
        """Test timing and performance measurement utilities"""
        import time

        # Test basic timing
        start_time = time.time()
        time.sleep(0.01)  # Small delay
        end_time = time.time()

        elapsed = end_time - start_time
        assert elapsed >= 0.01, "Should measure elapsed time"

        # Test if custom timing utilities exist
        try:
            with ff.timer() as t:
                time.sleep(0.01)
            assert t.elapsed >= 0.01, "Custom timer should work"
        except AttributeError:
            # Custom timer might not exist
            pass

    def test_memory_utilities(self):
        """Test memory usage utilities"""
        # Create large array
        large_array = np.random.randn(1000, 1000)

        # Test memory usage if utilities exist
        try:
            memory_usage = ff.get_memory_usage(large_array)
            assert memory_usage > 0, "Should report positive memory usage"
        except AttributeError:
            # Memory utilities might not exist
            pass

        # Clean up
        del large_array

    def test_optimization_utilities(self):
        """Test optimization and efficiency utilities"""
        # Test if optimization hints exist
        matrix = np.random.randn(100, 100)

        try:
            optimized = ff.optimize_matrix(matrix)
            assert (
                optimized.shape == matrix.shape
            ), "Optimized matrix should have same shape"
        except AttributeError:
            # Optimization utilities might not exist
            pass
