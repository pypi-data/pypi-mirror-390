# bool_extension_test.py

import unittest

from anb_python_components.extensions.bool_extension import *

class BoolExtensionTest(unittest.TestCase):
    def test_to_str (self):
        self.assertEqual(BoolExtension.to_str(True, "да", "нет"), "да")
        self.assertEqual(BoolExtension.to_str(False, "да", "нет"), "нет")
    
    def test_true_count (self):
        self.assertEqual(BoolExtension.true_count([False, True, False, True, True, False, False]), 3)
    
    def test_any_true (self):
        self.assertTrue(BoolExtension.any_true([False, True, False, True, True, False, False]))

if __name__ == '__main__':
    unittest.main()