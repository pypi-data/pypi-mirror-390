# array_extension_test.py

import unittest

from anb_python_components.extensions.array_extension import ArrayExtension


class ArrayExtensionTest(unittest.TestCase):
    def test_remove_empties(self):
        array = ["Мама", "Папа", "", "", "он", "", "она", "вместе", "", "дружная", "", "семья", ""]

        removed_empties = ["Мама", "Папа", "он", "она", "вместе", "дружная", "семья"]

        sorted_removed_empties = ["Мама", "Папа", "вместе", "дружная", "он", "она", "семья"]

        self.assertEqual(removed_empties, ArrayExtension.remove_empties(array))
        self.assertEqual(sorted_removed_empties, ArrayExtension.remove_empties(array, True))


if __name__ == '__main__':
    unittest.main()
