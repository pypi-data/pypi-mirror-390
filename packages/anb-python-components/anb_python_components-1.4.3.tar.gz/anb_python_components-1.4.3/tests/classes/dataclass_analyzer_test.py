# tests/dataclass_analyzer_test.py

import unittest
from dataclasses import dataclass, is_dataclass

from anb_python_components import DataClassExtension, DataclassAnalyzer

class Fields:
    @staticmethod
    def primary_key (default = None):
        return DataClassExtension.define(default, metadata = {'db_primary_key': True})
    
    @staticmethod
    def unique (default = None):
        return DataClassExtension.define(default, metadata = {'db_unique': True})
    
    @staticmethod
    def indexed (default = None):
        return DataClassExtension.define(default, metadata = {'db_indexed': True})
    
    @staticmethod
    def compose (default, *fields):
        return DataClassExtension.defines(default, *fields)

def table_name (name: str):
    """
    Декоратор для dataclass-класса, задающий имя таблицы в СУБД.
    :param name: Имя таблицы.
    :return: Обогащённый класс.
    """
    
    def decorator (cls):
        if not is_dataclass(cls):
            raise TypeError(f"Класс {cls.__name__} должен быть dataclass")
        
        # Сохраняем имя таблицы как атрибут класса (начинается с __meta_)
        cls.__meta_table_name = name
        return cls
    
    return decorator

@table_name("ANB")
@dataclass
class A:
    a: int = Fields.primary_key(0)
    b: str = Fields.compose("", Fields.unique(), Fields.indexed())

class DataclassAnalyzerTest(unittest.TestCase):
    def test_analyze (self):
        analyze_result = DataclassAnalyzer.analyze_class(A)
        self.assertEqual("ANB", analyze_result["__CLASS__"]["table_name"])
        self.assertTrue(analyze_result["a"]["db_primary_key"])
        
        analyze_result = DataclassAnalyzer.analyze_properties(A, "a")
        self.assertTrue(analyze_result["db_primary_key"])
        
        analyze_result = DataclassAnalyzer.analyze_properties(A, "b")
        self.assertTrue(analyze_result["db_unique"])
        self.assertTrue(analyze_result["db_indexed"])

if __name__ == '__main__':
    unittest.main()