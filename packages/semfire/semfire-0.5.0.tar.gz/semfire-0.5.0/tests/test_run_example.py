import unittest
import sys
from os import path

# Ensure the example script is in the python path
sys.path.append(path.abspath('integrations/navigator/examples'))

class TestRunExample(unittest.TestCase):

    def test_import(self):
        """
        Test that the run_example script can be imported without errors.
        """
        try:
            import run_example
        except ImportError as e:
            self.fail(f"Failed to import run_example: {e}")

    def test_main_function_exists(self):
        """
        Test that the main function exists in the run_example script.
        """
        import run_example
        self.assertTrue(hasattr(run_example, 'main'), "run_example.py should have a main function.")

if __name__ == '__main__':
    unittest.main()
