Contributing
============

We welcome contributions to the Free Fermion Library! This guide will help you get started.

Getting Started
---------------

Development Setup
~~~~~~~~~~~~~~~~~

1. Fork the repository on GitHub
2. Clone your fork locally::

    git clone https://github.com/yourusername/free-fermion-lib.git
    cd free-fermion-lib

3. Create a virtual environment::

    python -m venv dev-env
    source dev-env/bin/activate  # On Windows: dev-env\Scripts\activate

4. Install in development mode::

    pip install -e ".[dev]"

5. Install pre-commit hooks (optional but recommended)::

    pre-commit install

Running Tests
~~~~~~~~~~~~~

Run the test suite::

    pytest

Run tests with coverage::

    pytest --cov=src/ff --cov-report=html

Code Quality
~~~~~~~~~~~~

Format code with Black::

    black src/ tests/

Check code style::

    flake8 src/ tests/

Type checking::

    mypy src/ff/

Types of Contributions
----------------------

Bug Reports
~~~~~~~~~~~

When reporting bugs, please include:

* Your operating system and Python version
* Steps to reproduce the issue
* Expected vs actual behavior
* Minimal code example demonstrating the problem
* Full error traceback if applicable

Feature Requests
~~~~~~~~~~~~~~~~

For new features, please:

* Check if the feature already exists
* Describe the use case and motivation
* Provide a clear description of the desired functionality
* Consider backward compatibility

Code Contributions
~~~~~~~~~~~~~~~~~~

We accept contributions for:

* Bug fixes
* New algorithms and functions
* Performance improvements
* Documentation improvements
* Test coverage improvements

Development Guidelines
----------------------

Code Style
~~~~~~~~~~

* Follow PEP 8 style guidelines
* Use Black for code formatting (line length: 88 characters)
* Use meaningful variable and function names
* Add type hints where appropriate

Documentation
~~~~~~~~~~~~~

* All public functions must have docstrings
* Use NumPy-style docstrings
* Include examples in docstrings when helpful
* Update relevant documentation files

Testing
~~~~~~~

* Write tests for all new functionality
* Aim for high test coverage (>80%)
* Use descriptive test names
* Include edge cases and error conditions

Performance
~~~~~~~~~~~

* Consider computational complexity
* Use NumPy vectorization when possible
* Profile performance-critical code
* Document any performance considerations

Submitting Changes
------------------

Pull Request Process
~~~~~~~~~~~~~~~~~~~~

1. Create a new branch for your feature::

    git checkout -b feature-name

2. Make your changes and commit them::

    git add .
    git commit -m "Add feature: brief description"

3. Push to your fork::

    git push origin feature-name

4. Create a pull request on GitHub

Pull Request Guidelines
~~~~~~~~~~~~~~~~~~~~~~~

* Provide a clear description of the changes
* Reference any related issues
* Include tests for new functionality
* Ensure all tests pass
* Update documentation as needed
* Keep changes focused and atomic

Code Review Process
~~~~~~~~~~~~~~~~~~~

* All submissions require review
* Reviewers may request changes
* Address feedback promptly
* Be open to suggestions and improvements

Coding Standards
----------------

Function Documentation
~~~~~~~~~~~~~~~~~~~~~~

Use NumPy-style docstrings::

    def example_function(param1, param2=None):
        """
        Brief description of the function.
        
        Longer description if needed, explaining the algorithm,
        mathematical background, or implementation details.
        
        Parameters
        ----------
        param1 : array_like
            Description of param1
        param2 : int, optional
            Description of param2 (default: None)
            
        Returns
        -------
        result : ndarray
            Description of return value
            
        Raises
        ------
        ValueError
            When invalid input is provided
            
        Examples
        --------
        >>> result = example_function([1, 2, 3])
        >>> print(result)
        [1 4 9]
        
        Notes
        -----
        Additional notes about the implementation or mathematical
        background can go here.
        
        References
        ----------
        .. [1] Author, "Title", Journal, Year.
        """
        pass

Error Handling
~~~~~~~~~~~~~~

* Use appropriate exception types
* Provide informative error messages
* Validate input parameters
* Handle edge cases gracefully

Example::

    def validate_matrix(matrix):
        """Validate that input is a square matrix."""
        if not isinstance(matrix, np.ndarray):
            raise TypeError("Input must be a NumPy array")
        
        if matrix.ndim != 2:
            raise ValueError("Input must be a 2D array")
        
        if matrix.shape[0] != matrix.shape[1]:
            raise ValueError("Input must be a square matrix")

Testing Guidelines
------------------

Test Structure
~~~~~~~~~~~~~~

Organize tests by module::

    tests/
    ├── test_ff_lib.py
    ├── test_ff_combinatorics.py
    ├── test_ff_graph_theory.py
    └── test_ff_utils.py

Test Examples
~~~~~~~~~~~~~

::

    import pytest
    import numpy as np
    import ff

    class TestPfaffian:
        """Test pfaffian calculations."""
        
        def test_pfaffian_2x2(self):
            """Test pfaffian of 2x2 skew-symmetric matrix."""
            A = np.array([[0, 1], [-1, 0]])
            result = ff.pf(A)
            expected = 1.0
            assert abs(result - expected) < 1e-10
        
        def test_pfaffian_odd_dimension(self):
            """Test that pfaffian of odd-dimensional matrix is zero."""
            A = np.array([[0, 1, 2], [-1, 0, 3], [-2, -3, 0]])
            result = ff.pf(A)
            assert abs(result) < 1e-10
        
        def test_pfaffian_invalid_input(self):
            """Test error handling for invalid input."""
            with pytest.raises(TypeError):
                ff.pf("not a matrix")

Performance Testing
~~~~~~~~~~~~~~~~~~~

::

    import time
    import numpy as np
    import ff

    def test_performance_large_pfaffian():
        """Test performance for large matrices."""
        n = 100
        A = np.random.randn(n, n)
        A = A - A.T  # Make skew-symmetric
        
        start_time = time.time()
        result = ff.pf(A)
        elapsed = time.time() - start_time
        
        # Should complete within reasonable time
        assert elapsed < 10.0  # 10 seconds

Documentation Contributions
---------------------------

Building Documentation
~~~~~~~~~~~~~~~~~~~~~~

To build documentation locally::

    cd docs
    make html

The built documentation will be in ``docs/_build/html/``.

Documentation Style
~~~~~~~~~~~~~~~~~~~

* Use clear, concise language
* Include practical examples
* Explain mathematical concepts when relevant
* Cross-reference related functions
* Keep examples self-contained

Community Guidelines
--------------------

Code of Conduct
~~~~~~~~~~~~~~~

* Be respectful and inclusive
* Welcome newcomers and help them learn
* Focus on constructive feedback
* Respect different viewpoints and experiences

Communication
~~~~~~~~~~~~~

* Use GitHub issues for bug reports and feature requests
* Use GitHub discussions for questions and general discussion
* Be patient and helpful when answering questions
* Provide context and examples when asking for help

Recognition
-----------

Contributors will be acknowledged in:

* The project's AUTHORS file
* Release notes for significant contributions
* Documentation credits

Getting Help
------------

If you need help with development:

* Check existing issues and documentation
* Ask questions in GitHub discussions
* Reach out to maintainers for guidance
* Join community discussions

Thank you for contributing to the Free Fermion Library!