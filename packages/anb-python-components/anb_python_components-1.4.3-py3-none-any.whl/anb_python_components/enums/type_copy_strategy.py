# anb_python_components/enums/type_copy_strategy.py

from enum import Enum

class TypeCopyStrategy(Enum):
    """
    Стратегия копирования.
    Возможные значения:
        Ignore - без копирования.
        Auto - автоматический выбор.
        Copy - копирование (примитивы).
        DeepCopy - глубокое копирование (объекты и классы).
    """
    # Без стратегии копирования (простое присваивание).
    IGNORE = 0
    
    # Автоматически выбрать стратегию копирования (по типу объекта: COPY или DEEP_COPY).
    AUTO = 1
    
    # Копировать объект (хорошая практика для примитивов).
    COPY = 2
    
    # Глубокое копирование (для объектов и классов).
    DEEP_COPY = 3
    
    def __str__ (self):
        """
        Строковое представление объекта.
        :return: Строковое представление объекта.
        :rtype: str
        """
        # Итоговый текст
        text: str = ""
        
        # Выбор текста
        match self:
            case TypeCopyStrategy.IGNORE:
                text = "Без копирования"
            case TypeCopyStrategy.AUTO:
                text = "Автоматический выбор"
            case TypeCopyStrategy.COPY:
                text = "Обычное копирование (примитивы)"
            case TypeCopyStrategy.DEEP_COPY:
                text = "Глубокое копирование (объекты и классы)"
        
        # Возврат
        return text