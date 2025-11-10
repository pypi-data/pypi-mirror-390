# anb_python_components/classes/interface.py

import inspect
from functools import lru_cache
from typing import Any, Protocol, get_origin, runtime_checkable

@runtime_checkable
class Interface(Protocol):
    """
    Базовый класс для объявления интерфейсов с расширенной проверкой.
    """
    
    @classmethod
    @lru_cache(maxsize = 128)
    def verify (cls, obj_or_class) -> tuple[bool, list[str]]:
        """
        Проверяет, что объект или класс реализует интерфейс.
        :param obj_or_class: Объект (созданный класс) или класс (или, точнее, его имя), который должен реализовывать интерфейс.
        :return: Кортеж (is_ok, problems), где is_ok — True, если объект или класс реализует интерфейс, иначе False,
            а problems — список сообщений об ошибках, если is_ok == False.
        """
        # Разбираем аргумент на объект или имя класса. Если аргумент — имя класса, то получаем его класс. В противном случае,
        # возвращаем аргумент как объект.
        target = obj_or_class if isinstance(obj_or_class, type) else obj_or_class.__class__
        
        # Инициализируем список проблем
        problems = []
        
        # Собираем все методы интерфейса (включая унаследованные)
        interface_methods = cls._get_all_interface_methods()
        
        # Проходим по методам интерфейса
        for method_name, signature in interface_methods.items():
            # - если метод отсутствует в объекте
            if not hasattr(target, method_name):
                # -- добавляем в список проблем
                problems.append(f"отсутствует метод '{method_name}' / missing method '{method_name}'")
                # -- идём к следующему методу
                continue
            
            # - получаем именованный атрибут метода
            target_method = getattr(target, method_name)
            
            # - проверяем, что метод — вызываемый
            if not callable(target_method):
                # -- если нет, добавляем в список проблем
                problems.append(f"'{method_name}' it is not callable")
                # -- идём к следующему методу
                continue
            
            try:
                # - получаем сигнатуру метода
                target_signature = inspect.signature(target_method)
                
                # - сравниваем сигнатуры метода и интерфейса
                cls._compare_signatures(signature, target_signature, method_name, problems)
            except (ValueError, TypeError) as e:
                # Если сигнатуру нельзя получить, добавляем в список проблем
                problems.append(f"ошибка проверки сигнатуры / signature verification error '{method_name}': {e}")
        
        # В результат вернём кортеж (is_ok, problems), где is_ok — True, если проблем нет, иначе False, а problems — список проблем.
        return len(problems) == 0, problems
    
    @classmethod
    def check (cls, obj_or_class) -> bool:
        """
        Строгая проверка — поднимает исключение при несоответствии.
        :param obj_or_class: Объект (созданный класс) или класс (или, точнее, его имя), который должен реализовывать интерфейс.
        :return: True, если объект или класс реализует интерфейс.
        """
        # Проверяем, что объект или класс реализует интерфейс методом verify и получаем результат проверки
        is_ok, problems = cls.verify(obj_or_class)
        
        # Если объект или класс не реализует интерфейс
        if not is_ok:
            # - получаем имя объекта или класса
            target_name = obj_or_class.__name__ if isinstance(obj_or_class, type) else obj_or_class.__class__.__name__
            
            # - генерируем исключение с проблемами
            raise TypeError(
                    f"{target_name} не реализует интерфейс {cls.__name__}.\n" +
                    f"{target_name} not implements interface {cls.__name__}.\n" +
                    f"Проблемы / Problems:\n" +
                    "\n  ".join(problems)
                    )
        
        # Возвращаем True, если объект или класс реализует интерфейс
        return True
    
    @classmethod
    def get_methods (cls) -> dict[str, inspect.Signature]:
        """
        Возвращает словарь методов интерфейса с их сигнатурами.
        :return: Словарь методов интерфейса с их сигнатурами.
        """
        return cls._get_interface_methods(cls)
    
    @classmethod
    def _get_all_interface_methods (cls) -> dict[str, inspect.Signature]:
        """
        Собирает все методы из иерархии наследования интерфейсов.
        :return: Словарь методов с их сигнатурами.
        """
        # Создаем словарь методов
        methods = {}
        
        # Проходим по иерархии наследования интерфейсов рекурсивно
        for base in reversed(cls.__mro__):
            # - пропускаем базовый класс и сам интерфейс
            if base is Interface or not issubclass(base, Interface):
                continue
            
            # - добавляем методы базового интерфейса
            methods.update(cls._get_interface_methods(base))
        
        # Возвращаем собранные методы
        return methods
    
    @staticmethod
    def _get_interface_methods (interface_cls) -> dict[str, inspect.Signature]:
        """Извлекает методы интерфейса и их сигнатуры."""
        methods = {}
        for attr_name in dir(interface_cls):
            if attr_name.startswith('_') or attr_name == 'verify':
                continue
            attr = getattr(interface_cls, attr_name)
            if callable(attr):
                try:
                    signature = inspect.signature(attr)
                    methods[attr_name] = signature
                except (ValueError, TypeError):
                    # Если сигнатуру нельзя получить, оставляем пустую
                    methods[attr_name] = inspect.Signature()
        return methods
    
    @staticmethod
    def _compare_signatures (
            expected: inspect.Signature,
            actual: inspect.Signature,
            method_name: str,
            problems: list[str]
            ) -> None:
        """
        Сравнивает сигнатуры методов.
        :param expected: Ожидаемая сигнатура.
        :param actual: Текущая сигнатура.
        :param method_name: Имя метода.
        :param problems: Список проблем.
        :return: None
        """
        # Проверяем количество параметров
        expected_params = list(expected.parameters.values())
        actual_params = list(actual.parameters.values())
        
        # Проверяем количество параметров
        if len(expected_params) != len(actual_params):
            # - если количество параметров не совпадает, добавляем в список проблем
            problems.append(
                    f"'{method_name}': ожидается {len(expected_params)} параметров, получено {len(actual_params)} / {method_name}': expected {len(expected_params)} parameters, got {len(actual_params)}"
                    )
            
            # - прерываем выполнение
            return
        
        # Проверяем типы параметров (если указаны)
        for i, (exp_param, act_param) in enumerate(zip(expected_params, actual_params)):
            # - проверяем, что у ожидаемого параметра (exp_param) есть аннотация
            if exp_param.annotation is not exp_param.empty:
                # -- получаем тип ожидаемого параметра
                expected_type = exp_param.annotation
                # -- получаем тип текущего параметра
                actual_type = act_param.annotation if act_param.annotation is not act_param.empty else Any
                
                # -- сравниваем типы
                if get_origin(expected_type) != get_origin(actual_type):
                    # --- если типы не совпадают, добавляем в список проблем
                    problems.append(
                            f"Тип аннотации не совпадает для / annotation type mismatch for parameter '{exp_param.name}'"
                            )
    
    @classmethod
    def register (cls, target_class):
        """
        Регистрирует класс как реализующий интерфейс (для документации).
        :param target_class: Класс, который должен реализовывать интерфейс.
        :return: Регистрированный класс.
        """
        # Проверяем, что класс реализует интерфейс
        cls.check(target_class)
        
        # Возвращаем класс
        return target_class