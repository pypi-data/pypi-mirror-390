# anb_python_components/extensions/string_extension.py
import re

from .string_extension_constant import StringExtensionConstants

class StringExtension:
    """
    Расширение строк.
    """
    
    @staticmethod
    def is_none_or_empty (text: str | None) -> bool:
        """
        Проверяет, пуста ли строка.
        :param text: Проверяемая строка.
        :return: Результат проверки.
        """
        return text is None or text == ""
    
    @classmethod
    def is_none_or_whitespace (cls, text: str | None) -> bool:
        """
        Проверяет, пуста ли строка, содержит ли вместо текста только пробелы.
        :param text: Проверяемая строка.
        :return: Bool Результат проверки.
        """
        return cls.is_none_or_empty(text) or text.strip() == ''
    
    @staticmethod
    def is_russian_letter (letter: str) -> bool:
        """
        Проверяет, является ли символ русским буквой.
        :param letter: Проверяемый символ.
        :return: Результат проверки.
        """
        
        return letter in StringExtensionConstants.russian_letters
    
    @staticmethod
    def get_russian_letter_transliteration (letter: str) -> bool | None:
        """
        Получаю транслитерированную букву русского алфавита.
        :param letter: Буква русского алфавита.
        :return: Транслитерированная буква.
        """
        
        try:
            # Получаю транслитерированную букву
            transliteration = StringExtensionConstants.russian_letters[letter]
            
            # Если не удалось получить транслитерированную букву
            if transliteration is None:
                # - то возбуждаю исключение
                raise KeyError
        except KeyError:
            # Если возбуждено исключение, то возвращаю None
            return None
        
        # Возвращаю транслитерированную букву
        return transliteration
    
    @classmethod
    def convert_to_latin (cls, source: str) -> str:
        """
        Конвертация в латиницу.
        :param source: Исходная строка.
        :return: Результат перевода.
        """
        # Создаю результат
        result = ""
        
        # Получаю длину строкиДля каждой буквы или символа из слова
        for i, letter in enumerate(source):
            if cls.is_russian_letter(letter):
                # - транслитерирую эту букву
                result_transliteration = cls.get_russian_letter_transliteration(letter)
                
                # - если транслитерация не удалась
                if result_transliteration is None:
                    # -- вывожу оригинальную букву
                    result += letter
                else:
                    # -- вывожу транслитерированную букву
                    result += result_transliteration
            else:
                # - иначе вывожу букву или символ
                result += letter
        
        # Вывожу результат
        return result
    
    @classmethod
    def compare (cls, str1: str | None, str2: str | None, ignore_case: bool = False) -> int:
        """
        Сравнивает две строки.
        :param str1: Первая строка.
        :param str2: Вторая строка.
        :param ignore_case: Нужно ли учитывать регистр (по умолчанию, нет).
        :return: Результат сравнения. Возвращаемые значения:
                    -1 | значение str1 меньше значения str2.
                     0 | значения str1 и str2 равны.
                     1 | значение str1 больше значения str2.
        """
        # Если обе строки пусты
        if cls.is_none_or_whitespace(str1) and cls.is_none_or_whitespace(str2):
            # - то считаем их равными
            return 0
        
        # Если первый из них не пуст, а второй пуст
        if not cls.is_none_or_whitespace(str1) and cls.is_none_or_whitespace(str2):
            # - то первый больше
            return 1
        
        # Если первый из них пуст, а второй не пуст
        if cls.is_none_or_whitespace(str1) and not cls.is_none_or_whitespace(str2):
            # - то первый меньше
            return -1
        
        # Если не нужно учитывать регистр
        # - преобразую (или нет) первую строку
        compare_str_1 = str1 if not ignore_case else str1.lower()
        # - преобразую (или нет) вторую строку
        compare_str_2 = str2 if not ignore_case else str2.lower()
        
        # Проверяю равенство
        if compare_str_1 == compare_str_2:
            # - и если равны, то возвращаю 0
            return 0
        
        # Они не равны, поэтому получим длину первого слова и второго
        len1 = len(compare_str_1)
        len2 = len(compare_str_2)
        
        # Если длина первого больше и равна второго, то верну 1, иначе -1
        return 1 if len1 >= len2 else -1
    
    @staticmethod
    def get_short_text (text: str, max_length: int, end_symbols: str = '') -> str:
        """
        Обрезает строку до указанных в параметре max_length символов.
        :param text: Исходный текст.
        :param max_length: Максимальная длина текста.
        :param end_symbols: Суффикс, которым завершается обрезанная строка (по умолчанию, "").
        :return: Обрезанный текст.
        """
        # Если длина текста меньше максимальной
        if len(text) <= max_length:
            # - то возвращаем сам текст
            return text
        
        # Если длина текста больше максимальной, то получаю длину текста без суффикса
        len_no_end_symbols = max_length - len(end_symbols)
        
        # Возвращаю обрезанный текст
        return text[:len_no_end_symbols] + end_symbols
    
    @staticmethod
    def to_utf8 (subject: str, encoding: str = 'UTF-8') -> str:
        """
        Перекодирует строку в UTF-8.
        :param subject: Исходная строка.
        :param encoding: Исходная кодировка (по умолчанию, UTF-8).
        :return: Перекодированная строка.
        """
        # Если текущая кодировка уже UTF-8
        if encoding == 'UTF-8':
            # - то возвращаю исходную строку
            return subject
        
        # Получаем байты оригинальной строки
        bytes_original = subject.encode(encoding)
        
        # Преобразовываем в Unicode (используя указанную кодировку)
        unicode_string = bytes_original.decode(encoding)
        
        # Кодируем в UTF-8
        utf8_bytes = unicode_string.encode('UTF-8')
        
        # Возвращаем результат
        return utf8_bytes.decode('UTF-8')
    
    @staticmethod
    def from_utf8 (subject: str, to_encoding: str = 'UTF-8') -> str:
        """
        Перекодирует строку из UTF-8.
        :param subject: Исходная строка.
        :param to_encoding: Кодировка, в которую нужно перекодировать (по умолчанию, UTF-8).
        :return: Перекодированная строка.
        """
        # Если нужно перекодировать в UTF-8
        if to_encoding == 'UTF-8':
            # - то возвращаю исходную строку
            return subject
        
        # Получаю байты строки
        target_bytes = subject.encode('UTF-8')
        
        # Преобразовываю в нужную кодировку и возвращаю результат
        return str(target_bytes.decode('UTF-8').encode(to_encoding))
    
    @classmethod
    def replace (cls, subject: str, search: str, replace: str, encoding: str = 'UTF-8') -> str:
        """
        Заменяет в строке все вхождения строки поиска на строку замены.
        :param subject: Исходная строка.
        :param search: Строка поиска.
        :param replace: Строка замены.
        :param encoding: Кодировка (по умолчанию, UTF-8).
        :return: Результат замены.
        """
        # Если кодировка не UTF-8
        if encoding != 'UTF-8':
            # - то конвертирую все в UTF-8
            search = cls.to_utf8(search, encoding)
            replace = cls.to_utf8(replace, encoding)
            subject = cls.to_utf8(subject, encoding)
        
        # Список регулярных мета-символов (из документации re)
        special_chars = r'.^$*+?{}[]\|()'
        
        # Создаю список частей для регулярного выражения
        escaped_parts = []
        
        # Для каждой символа в строке поиска
        for char in search:
            # - экранируем только мета-символы re, остальные оставляем как есть
            if char in special_chars:
                escaped_parts.append(re.escape(char))
            else:
                escaped_parts.append(char)
        
        # Собираю регулярное выражение
        pattern = ''.join(escaped_parts)
        
        # Заменяю в строке
        result = re.sub(pattern, replace, subject)
        
        # Если кодировка не UTF-8
        if encoding != 'UTF-8':
            # - то конвертирую результат обратно в исходную кодировку
            result = cls.from_utf8(result, encoding)
        
        # Возвращаю результат
        return result
    
    @classmethod
    def replace_all (cls, search_replace: dict[str, str], subject: str, encoding: str = 'UTF-8') -> str:
        
        """
        Заменяет в строке все вхождения строки поиска на строку замены.
        :param search_replace: Словарь с парами поиска и замены. Например, {'-': '#', '$': '%'}
                                заменит все дефисы на # и все доллары на %.
        :param subject: Исходная строка.
        :param encoding: Кодировка (по умолчанию, UTF-8).
        :return: Результат замены.
        """
        # Создаю результат
        result = subject
        
        # Для каждой пары поиска и замены
        for search, replace in search_replace.items():
            # - заменяю все вхождения строки поиска на строку замены в заданной строке
            result = cls.replace(result, search, replace, encoding)
        
        # Возвращаю результат
        return result