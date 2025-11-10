# anb_python_components/extensions/bool_extension.py

from anb_python_components.enums.not_bool_action import NotBoolAction

class BoolExtension:
    """
    Расширение типа "правда/ложь".
    """
    
    def __init__ (self):
        """
        Инициализация расширения.
        """
        pass
    
    @staticmethod
    def to_str (b: bool, if_true: str = "True", if_false: str = "False") -> str:
        """
        Конвертирует булево значение в строку.
        :param b: Булево значение.
        :param if_true: Возвращаемое значение, если b == True (по умолчанию "True")
        :param if_false: Возвращаемое значение, если b == False (по умолчанию "False")
        :return: Строка, соответствующая булевому значению.
        """
        return if_true if b else if_false
    
    @staticmethod
    def true_count (expressions: list[bool], if_not_bool: NotBoolAction = NotBoolAction.IGNORE) -> int:
        """
        Возвращает количество истинных значений в списке аргументов.
        :param expressions: Список аргументов.
        :param if_not_bool: Действие при не булевом значении.
        :return: Количество истинных значений в списке аргументов.
        """
        # Создаем пустой массив для хранения проверяемых аргументов
        check_array = []
        
        # Проверяем все входящие аргументы
        for expression in expressions:
            # - если аргумент не является типом правда/ложь
            if not isinstance(expression, bool):
                match if_not_bool:
                    # -- если указано действие при не булевом значении - игнорирование
                    case NotBoolAction.IGNORE:
                        # - игнорируем аргумент и продолжаем цикл
                        continue
                    
                    # -- если указано действие при не булевом значении - считать как истинное значение
                    case NotBoolAction.IT_TRUE:
                        # --- добавляем True в массив проверяемых аргументов
                        check_array.append(True)
                        # --- и продолжаем цикл
                        continue
                    
                    # -- если указано действие при не булевом значении - считать как ложное значение
                    case NotBoolAction.IT_FALSE:
                        # --- добавляем False в массив проверяемых аргументов
                        check_array.append(False)
                        # --- и продолжаем цикл
                        continue
                    
                    # -- если указано действие при не булевом значении - выбросить исключение
                    case NotBoolAction.RAISE:
                        # --- то вызываем исключение
                        raise ValueError(f"{expression} не является булевым значением")
            else:
                # - иначе добавляем аргумент в массив проверяемых аргументов
                check_array.append(expression)
        
        # Используем фильтрацию массива для получения массива только истинных значений
        filtered = [value for value in check_array if value]
        
        # Возвращаем количество истинных значений в отфильтрованном массиве
        return len(filtered)
    
    @staticmethod
    def any_true (expressions: list[bool]) -> bool:
        """
        Проверяет, есть ли хотя бы один истинный аргумент.
        :param expressions: Выражения.
        :return: Есть ли хотя бы один истинный аргумент, то вернется True, иначе False.
        """
        # Получаем количество истинных значений
        true_count = BoolExtension.true_count(expressions, NotBoolAction.IGNORE)
        
        # Если количество истинных значений больше нуля, возвращаем True, иначе False
        return True if true_count > 0 else False