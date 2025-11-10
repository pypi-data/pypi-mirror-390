# anb_python_components/extensions/array_extension.py

from anb_python_components.extensions.string_extension import StringExtension

class ArrayExtension:
    """
    Класс расширения для работы с массивами.
    """
    
    def __init__ (self):
        """
        Инициализация расширения.
        """
        pass
    
    @staticmethod
    def remove_empties (array: list[str], re_sort: bool = False) -> list[str]:
        """
        Удаляет пустые строки из массива.

        :param array: Массив строк.
        :param re_sort: Пересортировать массив после удаления пустых строк.
        :return: Массив строк без пустых строк.
        """
        # Удаляем пустые строки
        result = list(filter(lambda x: not StringExtension.is_none_or_whitespace(x), array))
        
        # Если нужно пересортировать массив
        if re_sort:
            # - сортируем массив
            result.sort()
        
        # Возвращаем результат
        return result