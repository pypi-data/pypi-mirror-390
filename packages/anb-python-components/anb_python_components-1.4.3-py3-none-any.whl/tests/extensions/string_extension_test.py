# string_extension_test.py

import unittest

from anb_python_components.extensions.string_extension import *

class StringExtensionTest(unittest.TestCase):
    def test_is_none_or_empty (self):
        self.assertTrue(StringExtension.is_none_or_empty(None))
        self.assertTrue(StringExtension.is_none_or_empty(""))
        self.assertFalse(StringExtension.is_none_or_empty("Некий текст"))
        self.assertFalse(StringExtension.is_none_or_empty(" "))
    
    def test_is_none_or_whitespace (self):
        self.assertTrue(StringExtension.is_none_or_whitespace(None))
        self.assertTrue(StringExtension.is_none_or_whitespace(""))
        self.assertFalse(StringExtension.is_none_or_whitespace("Некий текст"))
        self.assertTrue(StringExtension.is_none_or_whitespace(" "))
    
    def test_is_russian_letter (self):
        self.assertTrue(StringExtension.is_russian_letter('п'))
        self.assertFalse(StringExtension.is_russian_letter("p"))
    
    def test_get_russian_letter_transliteration (self):
        self.assertEqual(StringExtension.get_russian_letter_transliteration('Ю'), 'Yu')
        self.assertNotEqual(StringExtension.get_russian_letter_transliteration('я'), 'Yu')
    
    def test_convert_to_latin (self):
        self.assertEqual(StringExtension.convert_to_latin('Россия'), 'Rossiya')
    
    def test_compare (self):
        self.assertEqual(StringExtension.compare('Россия', 'Россия'), 0)
        self.assertEqual(StringExtension.compare('Россия', 'Россия', True), 0)
        self.assertEqual(StringExtension.compare('Россия', 'россия', True), 0)
        self.assertEqual(StringExtension.compare('Россия', 'россия'), 1)
        self.assertEqual(StringExtension.compare('Россия - Великая держава', 'Россия'), 1)
        self.assertEqual(StringExtension.compare('Россия', 'Россия, мы гордимся Тобою'), -1)
    
    def test_get_short_text (self):
        self.assertEqual(StringExtension.get_short_text('Я люблю Python', 10), 'Я люблю Py')
        self.assertEqual(StringExtension.get_short_text('Я люблю Python', 10, '...'), 'Я люблю...')
    
    def test_replace (self):
        self.assertEqual(
                StringExtension.replace('Я люблю Python. Хотя только изучаю сам Python', 'Python', 'PHP'),
                "Я люблю PHP. Хотя только изучаю сам PHP"
                )
        self.assertEqual(
                StringExtension.replace('Я люблю #lang. Хотя только изучаю сам #lang', '#lang', 'Python'),
                "Я люблю Python. Хотя только изучаю сам Python"
                )
    
    def test_replace_all (self):
        self.assertEqual(
                StringExtension.replace_all(
                        {'#lang': 'Python', ':version': 'последнюю версию'},
                        'Я люблю #lang. Хотя только изучаю :version #lang'
                        ),
                "Я люблю Python. Хотя только изучаю последнюю версию Python"
                )

if __name__ == '__main__':
    unittest.main()