# directory_test.py

import unittest

from anb_python_components.classes.directory import Directory

class DirectoryTest(unittest.TestCase):
    def test_is_exists (self):
        self.assertTrue(Directory.is_exists(r"C:\Windows", "r"))
        self.assertFalse(Directory.is_exists(r"C:\Windows\1", "rw"))
        # Создайте поддиректорию 123 в директории теста и заполните ее содержимым
        self.assertTrue(Directory.is_exists(r".\123", "rwx"))
    
    def test_remove (self):
        # Создайте поддиректорию 123 в директории теста и заполните ее содержимым
        self.assertTrue(Directory.remove(r".\123"))

if __name__ == '__main__':
    unittest.main()