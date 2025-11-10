# anb_python_components/classes/shortcode_parser.py

import re
from typing import Callable, Dict

from anb_python_components.classes.action_state import ActionState
from anb_python_components.custom_types.shortcode_attributes import ShortCodeAttributes
from anb_python_components.models.shortcode_model import ShortCodeModel

class ShortCodeParser:
    """
    Класс для обработки текста на шорткоды.
    """
    
    # Список всех зарегистрированных шорткодов.
    __short_codes: Dict[str, dict[str, Callable]]
    
    def __init__ (self):
        """
        Инициализация парсера шорткодов.
        """
        self.__short_codes: Dict[str, dict[str, Callable]] = {}
    
    # noinspection PyUnusedLocal
    @staticmethod
    def default_set_unset (content: str, params: ShortCodeAttributes) -> str:
        """
        Функция по умолчанию для задания и удаления шорткодов.
        Просто возвращает неизмененный контент.
        :param content: Содержание шорткода.
        :type content: str
        :param params: Параметры шорткода.
        :type params: ShortCodeAttributes
        :return: Отформатированное содержимое.
        :rtype: str
        """
        return content
    
    # noinspection PyUnusedLocal
    @staticmethod
    def any_valid (content: str, params: ShortCodeAttributes) -> bool:
        """
        Метод проверки валидности шорткода, утверждающий, что шорткод валиден при любых условиях.
        :param content: Содержание шорткода.
        :type content: str
        :param params: Параметры шорткода.
        :type params: ShortCodeAttributes
        :return: Объект ActionState с результатом проверки валидности.
        :rtype: ActionState
        """
        return True
    
    def add_short_code (
            self, name: str, on_set: Callable | None = None, on_unset: Callable | None = None,
            on_validate: Callable | None = None
            ) -> None:
        """
        Добавляет новый шорткод.

        :param name: Название шорткода
        :type name: str
        :param on_set: Метод, вызываемый при обработке текста с включённым шорткодом
        :type on_set: Callable
        :param on_unset: Метод, вызываемый при обработке текста с отключённым шорткодом
        :type on_unset: Callable
        :param on_validate: Метод, вызываемый при проверке валидности шорткода
        :type on_validate: Callable
        :rtype: None
        """
        # Используем стандартные значения, если они не указаны
        on_set = on_set or self.default_set_unset
        on_unset = on_unset or self.default_set_unset
        on_validate = on_validate or self.any_valid
        
        # Сохраняем обработчики в словарь
        self.__short_codes[name] = {'set': on_set, 'unset': on_unset, 'validate': on_validate}
    
    def add_short_codes (self, short_codes: list[ShortCodeModel]) -> None:
        """
        Добавляет шорткоды из списка объектов ShortcodeModel.

        :param short_codes: Список объектов ShortcodeModel
        :type short_codes: list[ShortCodeModel]
        :rtype: None
        """
        # Для каждого шорткода
        for sc_model in short_codes:
            # - добавляем его в словарь
            self.add_short_code(sc_model.shortcode, sc_model.on_set, sc_model.on_unset, sc_model.on_validate)
    
    def __get_shortcode_regex (self) -> str:
        """
        Генерирует регулярное выражение для поиска шорткодов.
        
        :copyright: WordPress (сам шаблон).
        :link: https://developer.wordpress.org/plugins/shortcodes/
        :return: Регулярное выражение.
        :rtype: str
        """
        # Получаем список имён зарегистрированных шорткодов
        tag_names = list(self.__short_codes.keys())
        
        # Преобразуем каждое имя в экранированную версию (чтобы спецсимволы были защищены)
        quoted_tags = map(re.escape, tag_names)
        
        # Формируем теги для регулярного выражения
        tags = '|'.join(quoted_tags)
        
        # Создаём шаблон регулярного выражения для поиска шорткодов и выводим его
        return rf'\[(\[?)({tags})(?![\w-])([^\]\/]*(?:\/(?!\])[^\]\/]*)*?)(?:(\/)\]|\](?:([^\[]*+(?:\[(?!\/\2\])[^\[]*+)*+)\[\/\2\])?)(\]?)'
    
    def __handle_match (self, match: re.Match, ignore_included_shortcodes: bool = False, is_unset: bool = False) -> str:
        """
        Обрабатывает совпадение шорткода.
        :param match: Совпадение шорткода.
        :type match: re.Match
        :param ignore_included_shortcodes: Флаг игнорирования вложенных шорткодов.
        :type ignore_included_shortcodes: bool
        :param is_unset: Флаг удаления шорткода.
        :type is_unset: bool
        :return: Преобразованное содержание.
        :rtype: str
        """
        
        # Если совпадение не найдено
        if not match:
            # - то просто возвращаем контент
            return ''
        
        # Получаем имя шорткода
        tag_name = match.group(2).strip()
        # Получаем параметры шорткода
        attributes_str = str(match.group(3) or '').lstrip().rstrip()
        attributes = ShortCodeAttributes(attributes_str)
        # Получаем содержимое шорткода
        content = match.group(5) or ''
        
        # Если текущая глубина вложенности не превышает ЗАДАННУЮ максимальную или максимальная глубина не задана
        if not ignore_included_shortcodes:
            # - то вызываем рекурсию
            content = self.parse(content, False, is_unset)
        
        # Если шорткод не зарегистрирован
        if tag_name not in self.__short_codes:
            # - то просто возвращаем его
            return f'[{match}]'
        
        # Получаем функцию валидации
        validate_function = self.__short_codes[tag_name].get('validate') or self.any_valid
        
        # Валидируем контент шорткода
        validation_result = validate_function(content, attributes)
        
        # Если валидация не прошла
        if not validation_result:
            # - то возвращаем контент
            return f'{match}'
        
        # Получаем функции обработки
        # - если шорткод устанавливается
        set_function = self.__short_codes[tag_name].get('set') or self.default_set_unset
        # - если шорткод удаляется
        unset_function = self.__short_codes[tag_name].get('unset') or self.default_set_unset
        
        # Выбираем функцию обработки
        function = set_function if not is_unset else unset_function
        
        # Возвращаем обработанный контент
        return function(content, attributes)
    
    def parse (self, content: str, ignore_included_shortcodes: bool = False, is_unset: bool = False) -> str:
        """
        Производит поиск и обработку шорткодов в тексте.
    
        :param content: Исходный текст.
        :type content: str
        :param ignore_included_shortcodes: Флаг игнорирования вложенных шорткодов.
        :type ignore_included_shortcodes: bool
        :param is_unset: Флаг удаления шорткода.
        :type is_unset: bool
        :return: Преобразованный текст.
        :rtype: str
        """
        
        # Получаем регулярное выражение для поиска шорткодов
        regex = self.__get_shortcode_regex()
        
        # Заменяем все найденные шорткоды
        result = re.sub(
                regex, lambda match: self.__handle_match(match, ignore_included_shortcodes, is_unset), content,
                flags = re.MULTILINE | re.IGNORECASE | re.VERBOSE
                )
        
        # Возвращаем результат
        return result