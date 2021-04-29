"""
Run all tests associated with this package.
Run by executing Python3 run_all_tests.py (do not use -m)
"""

import sys
import unittest

if __name__ == '__main__':
    test_suite = unittest.defaultTestLoader.discover('manifest_lambda/tests/unit', 'test_*.py')
    test_runner = unittest.TextTestRunner(resultclass=unittest.TextTestResult)
    result = test_runner.run(test_suite)
    # specify an exit code for integrations with CI
    sys.exit(not result.wasSuccessful())
