# anb_python_components/classes/dataclass_analyzer.py
from dataclasses import fields, is_dataclass
from typing import Any

class DataclassAnalyzer:
    """
    Класс анализа классов отмеченных как dataclass.
    """
    
    @staticmethod
    def analyze_properties (cls, prop_name: str) -> dict[str, Any]:
        """
        Анализирует декораторы (метаданные) указанного свойства класса.
        :param cls: Класс (должен реализовывать dataclass).
        :param prop_name: Имя свойства.
        :return: Словарь с информацией о применённых декораторах.
        """
        # Проверяем, что класс является dataclass
        if not is_dataclass(cls):
            # - иначе бросаем исключение
            raise TypeError(f"Класс {cls.__name__} не является dataclass / Class {cls.__name__} is not a dataclass")
        
        # Находим поле по имени
        # - задаём начальное значение None
        field_obj = None
        
        # Перебираем поля класса
        for field in fields(cls):
            # - ищем поле с указанным именем
            if field.name == prop_name:
                # - если нашли, сохраняем объект поля
                field_obj = field
                # - и выходим из цикла
                break
        
        # Если поле не найдено
        if field_obj is None:
            # - бросаем исключение
            raise AttributeError(
                    f"Свойство '{prop_name}' не найдено в классе {cls.__name__} / Property '{prop_name}' not found in class {cls.__name__}"
                    )
        
        # Создаем словарь для результатов
        results = {}
        
        # Собираем метаданные
        metadata = field_obj.metadata or {}
        
        # Перебираем метаданные
        for key, value in metadata.items():
            # - добавляем в словарь
            results[key] = value
        
        # Возвращаем результаты
        return results
    
    @staticmethod
    def analyze_class (cls) -> dict[str, dict[str, Any]]:
        """
        Анализирует все свойства dataclass-класса и класс‑уровневые метаданные.
        :param cls: Dataclass-класс.
        :return: Словарь с метаданными полей и класса.
        """
        # Проверяем, что класс является dataclass
        if not is_dataclass(cls):
            # - иначе бросаем исключение
            raise TypeError(f"Класс {cls.__name__} не является dataclass / Class {cls.__name__} is not a dataclass")
        
        results = {}
        
        # Собираем класс‑уровневые метаданные (всё, что начинается с __meta_)
        # - создаём пустой словарь
        class_metadata = {}
        
        # Перебираем атрибуты класса
        for attr_name in dir(cls):
            # - ищем атрибуты, начинающиеся с __meta_
            if attr_name.startswith("__meta_"):
                # -- удаляем префикс __meta_ и берём значение
                key = attr_name[len("__meta_"):]
                # -- добавляем в словарь
                class_metadata[key] = getattr(cls, attr_name)
        
        # Если есть метаданные
        if class_metadata:
            # - добавляем в результаты
            results["__CLASS__"] = class_metadata
        
        # Анализируем каждое поле
        for field in fields(cls):
            # - получаем имя поля
            field_name = field.name
            # - анализируем поле и сохраняем результаты в словарь
            results[field_name] = DataclassAnalyzer.analyze_properties(cls, field_name)
        
        # Возвращаем результаты
        return results