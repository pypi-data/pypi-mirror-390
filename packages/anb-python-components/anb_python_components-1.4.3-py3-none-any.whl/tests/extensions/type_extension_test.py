# type_extension_test.py

import unittest

from anb_python_components.extensions.type_extension import TypeExtension
from anb_python_components.custom_types.guid import GUID

class DemoClass:
    def __init__ (self, name):
        self.name = name
        self.age = 20

class TypeExtensionTest(unittest.TestCase):
    
    def test_to_dict (self):
        converted = TypeExtension.to_dict(DemoClass('Иван'))
        self.assertEqual(converted, {'name': 'Иван', 'age': 20})
    
    def test_from_dict (self):
        # Представим данные в виде словаря
        data = {'name': 'Иван', 'age': 20}
        
        # Преобразуем данные в объект DemoClass
        converted = TypeExtension.from_dict(data, DemoClass)
        
        # Проверяем, что полученный объект является экземпляром DemoClass
        self.assertIsInstance(converted, DemoClass)
        
        # Проверяем, что объект содержит ожидаемые значения
        self.assertEqual(converted.name, 'Иван')
        self.assertEqual(converted.age, 20)
    
    def test_is_immutable_type (self):
        self.assertTrue(TypeExtension.is_immutable_type(int))
        self.assertFalse(TypeExtension.is_immutable_type(GUID))

if __name__ == '__main__':
    unittest.main()