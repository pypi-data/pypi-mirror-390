# file_test.py

import unittest

from anb_python_components.classes.file import File

class FileTest(unittest.TestCase):
    def test_is_exists (self):
        file_name = r"C:\Windows\explorer.exe"
        dir_name = r"C:\Windows"
        self.assertTrue(File.is_exist(file_name))
        self.assertFalse(File.is_exist(dir_name))
    
    def test_find (self):
        find_list = File.find(r"..\classes", "*.py")
        result = [
                '..\\classes\\action_state_test.py', '..\\classes\\directory_test.py', '..\\classes\\file_test.py',
                '..\\classes\\__init__.py'
                ]
        
        self.assertEqual(result, find_list)
    
    def test_extract_file_name (self):
        file_name = r"C:\Windows\explorer.exe"
        result = File.extract_file_name(file_name)
        expected_result = "explorer.exe"
        
        self.assertEqual(expected_result, result)
    
    def test_extract_file_extension (self):
        file_name = r"C:\Windows\explorer.exe"
        result = File.extract_file_extension(file_name)
        expected_result = ".exe"
        
        self.assertEqual(expected_result, result)
        
        result = File.extract_file_extension(file_name, False)
        expected_result = "exe"
        
        self.assertEqual(expected_result, result)
    
    def test_extract_file_name_without_extension (self):
        file_name = r"C:\Windows\explorer.exe"
        result = File.extract_file_name_without_extension(file_name)
        expected_result = "explorer"
        
        self.assertEqual(expected_result, result)
    
    def test_relative_path (self):
        file_name = r"C:\Windows\explorer.exe"
        result = File.relative_path(file_name, r"C:\Windows")
        expected_result = r"\explorer.exe"
        
        self.assertEqual(expected_result, result)
    
    def test_size (self):
        file_name = r"C:\Windows\explorer.exe"
        result = File.size(file_name).value
        expected_result = 2774080
        
        self.assertEqual(expected_result, result)
    
    def test_size_to_string (self):
        file_name = r"C:\Windows\explorer.exe"
        size = File.size(file_name).value
        result = File.size_to_string(size)
        expected_result = "2.65 МБ"
        
        self.assertEqual(expected_result, result)
    
    def test_hash (self):
        file_name = r"C:\Windows\explorer.exe"
        result = File.hash(file_name)
        expected_result = "6345f80dd23b51d90bfdedfe03c51c9d85c5233c9fb2f2cfe9e1ac633a4895ca"
        
        self.assertEqual(expected_result, result)

if __name__ == '__main__':
    unittest.main()