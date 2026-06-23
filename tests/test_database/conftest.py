"""conftest for test_database package.

Registers custom pytest marks:
- slow: tests that take a long time (large file I/O)
"""

import pytest

pytest.register_assert_rewrite("tests.test_database.helpers")

pytest.mark.slow  # make pyflakes happy; actual registration is in pyproject.toml
