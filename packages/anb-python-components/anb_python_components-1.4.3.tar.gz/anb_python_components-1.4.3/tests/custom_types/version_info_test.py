# tests/custom_types/version_info_test.py

import unittest

from anb_python_components.custom_types.version_info import VersionInfo

class VersionInfoTest(unittest.TestCase):
    def test_init (self):
        version_info = VersionInfo(1, 2, 3, 4, "Тестовая версия", 1)
        version_info_str = '1.2.3.4 Тестовая версия 1'
        
        self.assertEqual(version_info_str, str(version_info))
    
    def test_math (self):
        version_info_1 = VersionInfo(1, 2, 3, 4, "Тестовая версия", 1)
        version_info_2 = VersionInfo(1, 2, 3, 4, "Тестовая версия", 1)
        version_info_3 = VersionInfo(2, 1, 3, 10, "Тестовая версия", 2)
        version_info_4 = VersionInfo(3, 5, 3, 12, "Тестовая версия", 3)
        
        self.assertTrue(version_info_1 == version_info_2)
        self.assertTrue(version_info_3 > version_info_2)
        self.assertTrue(version_info_3 >= version_info_1)
        self.assertTrue(version_info_1 < version_info_4)
        self.assertTrue(version_info_3.in_range(version_info_1, version_info_4))
        self.assertFalse(version_info_3.in_range(version_info_1, version_info_3, end_inclusive = False))
        self.assertTrue(version_info_3.in_range(version_info_1))
        self.assertTrue(version_info_3.in_range())
    
    def test_parse (self):
        str_ver_1 = '1.2.3.4 Тестовая 1'
        version_info_1 = VersionInfo(1, 2, 3, 4, "Тестовая", 1)
        str_ver_2 = "1.2.3.4 Тестовая"
        version_info_2 = VersionInfo(1, 2, 3, 4, "Тестовая", 0)
        str_ver_3 = "1.2.3.4"
        version_info_3 = VersionInfo(1, 2, 3, 4, "", 0)
        str_ver_4 = "1.2.3 Тестовая 1"
        version_info_4 = VersionInfo(1, 2, 3, 0, "Тестовая", 1)
        str_ver_5 = "1.2 Тестовая 1"
        version_info_5 = VersionInfo(1, 2, 0, 0, "Тестовая", 1)
        str_ver_6 = "1 Тестовая 1"
        version_info_6 = VersionInfo(1, 0, 0, 0, "Тестовая", 1)
        
        self.assertEqual(version_info_1, VersionInfo.parse(str_ver_1))
        self.assertEqual(version_info_2, VersionInfo.parse(str_ver_2))
        self.assertEqual(version_info_3, VersionInfo.parse(str_ver_3))
        self.assertEqual(version_info_4, VersionInfo.parse(str_ver_4))
        self.assertEqual(version_info_5, VersionInfo.parse(str_ver_5))
        self.assertEqual(version_info_6, VersionInfo.parse(str_ver_6))

if __name__ == '__main__':
    unittest.main()