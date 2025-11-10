# tests/custom_types/two_dim_size_test.py

import unittest

from anb_python_components.custom_types.two_dim_size import TwoDimSize

class TwoDimSizeTest(unittest.TestCase):
    def test_init (self):
        size = TwoDimSize(1, 2)
        
        self.assertEqual(size.width, 1)
        self.assertEqual(size.height, 2)
        
        size = TwoDimSize(1, 5, 3, max_height = 4)
        self.assertEqual(size.width, 3)
        self.assertEqual(size.height, 4)
    
    def test_math (self):
        size_1 = TwoDimSize(1, 2)
        size_2 = TwoDimSize(3, 4)
        size_3 = size_1 + size_2
        
        self.assertEqual(size_3.width, 4)
        self.assertEqual(size_3.height, 6)
        
        self.assertTrue(size_3 == TwoDimSize(4, 6))
    
    def test_parse (self):
        str_size = "1x2"
        
        size = TwoDimSize.parse(str_size, 'x')
        
        self.assertEqual(size.width, 1)
        self.assertEqual(size.height, 2)

if __name__ == '__main__':
    unittest.main()