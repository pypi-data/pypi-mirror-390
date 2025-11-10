# anb_python_components/extensions/type_extension.py

import datetime
from typing import Any, List, Union, get_args, get_origin

# Базовая структура для представления расширенного типа
class TypeExtension:
    """
    Класс для расширения типов.
    """
    
    def __init__ (self):
        """
        Инициализирует экземпляр класса.
        """
        pass
    
    @staticmethod
    def to_dict (instance: Any) -> dict[str, Any]:
        """
        Преобразует экземпляр объекта в словарь.

        :param instance: Экземпляр класса.
        :return: Словарь представлений всех полей.
        """
        # Создаём словарь
        result = {}
        
        # Перебираем поля экземпляра
        for key, value in vars(instance).items():
            # - если значение является экземпляром datetime, преобразуем его в timestamp
            if isinstance(value, datetime.datetime):
                result[key] = int(value.timestamp())
                # - если значение является словарем, вызываем рекурсивно функцию to_dict
            elif hasattr(value, '__dict__'):
                result[key] = TypeExtension.to_dict(value)
                # - иначе просто добавляем значение
            else:
                result[key] = value
        
        # Возвращаем словарь
        return result
    
    @staticmethod
    def from_dict (data: dict, cls = None) -> Any:
        """
        Восстанавливает объект из словаря.

        :param data: Словарь, представляющий поля объекта.
        :param cls: Класс для восстановления объекта (необязательный параметр, равный None по умолчанию).
        :return: Восстановленный объект.
        """
        
        # Проверяем, что класс указан и является типом
        if cls is None or not isinstance(cls, type):
            # - если класс не указан, бросаем исключение
            raise TypeError('Класс для восстановления не указан.')
        
        # Создаём объект класса
        # noinspection PyArgumentList
        obj = cls.__new__(cls)
        
        # Перебираем поля словаря
        for key, value in data.items():
            # - если значение является словарем, вызываем рекурсивно функцию from_dict и устанавливаем результат в поле объекта
            if isinstance(value, int) and hasattr(obj, key) and isinstance(getattr(obj, key), datetime.datetime):
                setattr(obj, key, datetime.datetime.fromtimestamp(value))
            elif isinstance(value, dict):
                nested_cls = getattr(obj, key).__class__
                setattr(obj, key, TypeExtension.from_dict(value, nested_cls))
            else:
                setattr(obj, key, value)
        
        # Возвращаем восстановленный объект
        return obj
    
    @staticmethod
    def is_immutable_type (t) -> bool:
        """
        Проверяет, является ли тип t примитивным/неизменяемым.
        :param t: Тип.
        :type t: type
        :return: True, если тип является примитивным/неизменяемым, иначе False.
        """
        # Примитивные неизменяемые типы
        immutable_types = (int, str, float, bool, type(None), tuple, frozenset)
        
        # Прямая проверка на примитивы
        if t in immutable_types:
            return True
        
        # Обработка Union
        if get_origin(t) is Union:
            args = get_args(t)
            
            # Если это Optional[T] (Union[T, None])
            if len(args) == 2 and type(None) in args:
                inner_type = args[0] if args[1] is type(None) else args[1]
                return TypeExtension.is_immutable_type(inner_type)  # Рекурсивно проверяем T
            
            # Для обычного Union проверяем все аргументы
            return all(TypeExtension.is_immutable_type(arg) for arg in args)
        
        # Обработка list[T], List[T]
        if get_origin(t) in (list, List):
            args = get_args(t)
            if not args:  # list без параметра (list)
                return False  # Считаем изменяемым
            inner_type = args[0]  # Получаем T из list[T]
            return TypeExtension.is_immutable_type(inner_type)  # Проверяем T
        
        return False
    
    @staticmethod
    def check_immutability (value: Any) -> bool:
        """
        Проверяет, является ли значение `value` неизменяемым по типу.
        :param value: Проверяемое значение.
        :return: True, если тип значения неизменяемый, иначе False.
        """
        # None — неизменяемый
        if value is None:
            return True
        
        # Получаем фактический тип значения
        value_type = type(value)
        
        # Используем get_origin/get_args для анализа
        origin = get_origin(value_type)
        
        # Если это параметризованный тип (list[int], Union[str, int] и т.п.),
        if origin is not None:
            # - передаём сам параметризованный тип в is_immutable_type
            return TypeExtension.is_immutable_type(origin)
        else:
            # - иначе проверяем тип напрямую (для простых типов, таких как int, str и т.п.)
            return TypeExtension.is_immutable_type(value_type)