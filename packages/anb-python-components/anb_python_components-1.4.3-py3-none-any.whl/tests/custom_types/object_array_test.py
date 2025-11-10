# tests/custom_types/object_array_test.py

import unittest
from dataclasses import dataclass, field

from anb_python_components.custom_types.object_array import ObjectArray

@dataclass
class TestClass:
    key: int = field(default = 0)
    value: int = field(default = 0)

class ObjectArrayTest(unittest.TestCase):
    def test_init (self):
        array = ObjectArray[int]([1, 2, 3])
        self.assertEqual(3, len(array))
    
    @staticmethod
    def _create_array () -> ObjectArray[int]:
        return ObjectArray[int]([1, 2, 3])
    
    def test_get (self):
        array = self._create_array()
        item = array[0]
        self.assertEqual(1, item)
    
    def test_set (self):
        array = self._create_array()
        array[0] = 4
        self.assertEqual(4, array[0])
    
    def test_add (self):
        array = self._create_array()
        array.add(4)
        self.assertEqual(4, array[3])
    
    def test_add_range (self):
        array = self._create_array()
        array.add_range([4, 5, 6])
        self.assertEqual(4, array[3])
        self.assertEqual(6, len(array))
    
    def test_to_array (self):
        array = self._create_array()
        
        self.assertEqual([1, 2, 3], array.to_array())
    
    def test_find (self):
        array = self._create_array()
        self.assertEqual(3, array.find(3))
    
    def test_sort (self):
        array = ObjectArray[TestClass](
                [
                        TestClass(1, 3),
                        TestClass(3, 2),
                        TestClass(2, 1)
                        ]
                )
        array.sort('key')
        self.assertEqual(2, array[1].key)
    
    def test_sort_callback (self):
        array = self._create_array()
        array.sort_callback(lambda a: a, True)
        self.assertEqual(3, array[0])
    
    def test_count (self):
        array = self._create_array()
        
        self.assertEqual(1, array.count(lambda a: a == 1))
    
    def test_is_exists (self):
        array = self._create_array()
        is_exists = array.is_exists(lambda a: a == 3)
        non_exists = array.is_exists(lambda a: a == 4)
        self.assertTrue(is_exists)
        self.assertFalse(non_exists)
    
    def test_min_max (self):
        array = self._create_array()
        self.assertEqual(1, array.min(lambda a: a))
        self.assertEqual(3, array.max(lambda a: a))
    
    def test_get_rows (self):
        array = self._create_array()
        self.assertEqual(2, len(array.get_rows(lambda a: a != 2)))
        self.assertEqual(3, len(array.get_rows()))
    
    def test_get_row (self):
        array = self._create_array()
        self.assertEqual(3, array.get_row(lambda a: a == 3))
    
    def test_where (self):
        array = self._create_array()
        self.assertEqual(3, array.where(lambda a: a == 3).first(0))
        self.assertEqual(None, array.where(lambda x: x == 4).first(None))
        self.assertEqual(2, len(array.where(lambda a: a != 2)))
    
    def test_get_column (self):
        array = ObjectArray[TestClass](
                [
                        TestClass(1, 3),
                        TestClass(3, 2),
                        TestClass(2, 1)
                        ]
                )
        
        get_column1 = array.get_column('key')
        get_column2 = array.get_column('key', lambda a: a.key != 3)
        
        self.assertEqual([1, 3, 2], get_column1.to_array())
        self.assertEqual([1, 2], get_column2.to_array())
    
    def test_get_column_callback (self):
        array = ObjectArray[TestClass](
                [
                        TestClass(1, 3),
                        TestClass(3, 2),
                        TestClass(2, 1)
                        ]
                )
        
        get_column_callback = array.get_column_callback(
                lambda a: a.value,
                lambda a: a.key != 3
                )
        
        self.assertEqual([3, 1], get_column_callback.to_array())
    
    def test_get_value (self):
        array = ObjectArray[TestClass](
                [
                        TestClass(1, 3),
                        TestClass(3, 2),
                        TestClass(2, 1)
                        ]
                )
        
        self.assertEqual(2, array.get_value('value', lambda a: a.key == 3))
    
    def test_delete (self):
        array = self._create_array()
        
        array.delete(lambda a: a == 2)
        self.assertEqual(2, len(array))
        
        array.delete()
        self.assertEqual(0, len(array))
    
    def test_first_and_last (self):
        array = self._create_array()
        
        self.assertEqual(1, array.first(0))
        self.assertEqual(3, array.last(0))
    
    def test_skip (self):
        array = self._create_array()
        
        self.assertEqual([2, 3], array.skip(1).to_array())
    
    def test_take (self):
        array = self._create_array()
        
        self.assertEqual([1, 2], array.take(2).to_array())
    
    def test_skip_and_take (self):
        array = self._create_array()
        
        self.assertEqual([2], array.skip(1).take(1).to_array())

if __name__ == '__main__':
    unittest.main()