# anb_python_components/decorators/interface_decorators.py
import inspect
from typing import Callable

from anb_python_components import Interface

def interface_required (signature: Callable | None = None, **kwargs) -> Callable:
    """
    Декоратор для явного указания обязательных методов интерфейса.
    Позволяет задать сигнатуру через аннотации.
    """
    
    def decorator (func) -> Callable:
        """
        Декоратор для проверки сигнатуры.
        :param func: Функция для проверки.
        :return: Проверенная функция.
        """
        # Если сигнатура указана
        if signature is not None:
            # - сохраняем сигнатуру в атрибуте сигнатуры
            func.__signature__ = inspect.signature(signature)
        else:
            # - иначе сохраняем сигнатуру в атрибуте аннотаций
            func.__annotations__ = kwargs
        
        # Возвращаем функцию
        return func
    
    # Возвращаем функцию-декоратор
    return decorator

def implement (interface):
    """
    Декоратор для явного указания реализации интерфейса.
    :param interface: Класс-интерфейс (наследник Interface)
    :raise: TypeError: если класс не реализует интерфейс
    :return: Оригинальный класс (с добавленным атрибутом __implements__)
    """
    
    def decorator (cls):
        """
        Декоратор для реализации интерфейса.
        :param cls: Класс для реализации интерфейса.
        :return: Оригинальный класс с реализацией интерфейса.
        """
        # 1. Проверяем, что interface действительно является интерфейсом
        if not isinstance(interface, type) or not issubclass(interface, Interface):
            raise TypeError(
                    f"{interface} не является интерфейсом (не наследуется от Interface) / is not an interface (does not inherit from Interface)"
                    )
        
        # 2. Выполняем строгую проверку реализации
        try:
            interface.check(cls)
        except TypeError as e:
            raise TypeError(
                    f"Класс {cls.__name__} не реализует интерфейс {interface.__name__} / class {cls.__name__} does not implement interface {interface.__name__}\n  {e}"
                    ) from e
        
        # 3. Добавляем метаданные о реализации
        if not hasattr(cls, '__implements__'):
            cls.__implements__ = []
        cls.__implements__.append(interface)
        
        # 4. Сохраняем ссылку на интерфейс для интроспекции
        impl_attr = f'__implements_{interface.__name__}'
        setattr(cls, impl_attr, True)
        
        # 5. Декоратор должен вернуть оригинальный класс
        return cls
    
    # Возвращаем функцию-декоратор
    return decorator