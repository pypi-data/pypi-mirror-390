from dataclasses import dataclass, field
from typing import Callable

@dataclass
class ShortCodeModel:
    """
    Модель добавления шорткода.
    """
    # Буква, символ или последовательность символов, которая будет использоваться для шорткода.
    # Если не указана, то будет использована пустая строка.
    shortcode: str = field(default = '')
    
    # Обработчик действия шорткода при обработке текста, когда шорткод включен.
    # Функция должна принимать два аргумента: content (str) и params (dict).
    on_set: Callable | None = field(default_factory = lambda: None)
    
    # Обработчик действия шорткода при обработке текста, когда шорткод отключен.
    # Аналогично OnSet.
    on_unset: Callable | None = field(default_factory = lambda: None)
    
    # Обработчик действия шорткода при валидации самого шорткода.
    # Функционал тот же, что и у OnSet и OnUnSet.
    on_validate: Callable | None = field(default_factory = lambda: None)