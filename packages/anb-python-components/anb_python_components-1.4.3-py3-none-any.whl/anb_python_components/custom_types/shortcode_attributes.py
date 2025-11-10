# anb_python_components/custom_types/shortcode_attributes.py

class ShortCodeAttributes:
    """
    Атрибуты шорткода.
    """
    
    # Словарь атрибутов шорткода (ключ - имя атрибута, значение - значение атрибута)
    __attributes: dict[str, str] = {}
    
    def __init__ (self, attributes: dict[str, str] | str | None = None):
        """
        Конструктор.
        :param attributes: Атрибуты шорткода в виде словаря, строки или None. В случае None - атрибуты будут заданы пустым словарем.
            По умолчанию None.
        """
        # Инициализируем словарь
        self.__attributes = {}
        
        # Если атрибуты не заданы
        if attributes is None:
            # - то выходим из функции
            return
        
        # Если атрибуты заданы как строка
        if isinstance(attributes, str):
            # - разделяем параметры по пробелам
            pairs = attributes.split()
            
            # - для каждого параметра
            for pair in pairs:
                # -- разбиваем его на ключ и значение
                key_value = pair.split('=', 1)
                
                # -- если количество элементов не равно 2
                if len(key_value) != 2:
                    # --- то пропускаем
                    continue
                
                # -- задаем ключ и знач
                key, value = key_value
                
                # -- записываем ключ и значение в словарь, предварительно убирая кавычки и пробелы с обеих сторон
                self.__attributes[key.lstrip().rstrip()] = value.lstrip(' "').rstrip('" ')
        
        # Если атрибуты заданы как словарь
        if isinstance(attributes, dict):
            # - для каждого ключа и значения
            for key, value in attributes.items():
                # -- записываем ключ и значение в словарь
                self.__attributes[key] = value
    
    @staticmethod
    def parse (param_string: str) -> 'ShortCodeAttributes':
        """
        Преобразует строку параметров в словарь.
    
        :param param_string: Строка параметров
        :return: Словарь параметров
        """
        # Возвращаем словарь параметров
        return ShortCodeAttributes(param_string)
    
    def __str__ (self) -> str:
        """
        Преобразует атрибуты в строку.
        :return: Строка атрибутов.
        """
        # Если атрибуты не заданы
        if not self.__attributes:
            # - то возвращаем пустую строку
            return ''
        
        # Возвращаем строку
        return ' '.join([f'{key}="{value}"' for key, value in self.__attributes.items()])
    
    def __iter__ (self):
        """
        Итератор.
        :return: Итератор.
        """
        return iter(self.__attributes.items())
    
    def __getitem__ (self, key: str) -> str | None:
        """
        Доступ к атрибутам по ключу.
        :param key: Ключ атрибута.
        :return: Значение атрибута или None, если атрибут не найден.
        """
        return self.__attributes[key] if key in self.__attributes else None
    
    def __setitem__ (self, key: str, value: str):
        """
        Установить значение атрибута.
        :param key: Ключ атрибута.
        :param value: Значение атрибута.
        :return: None
        """
        self.__attributes[key] = value
    
    def __contains__ (self, key: str) -> bool:
        """
        Проверяет наличие атрибута.
        :param key: Ключ атрибута.
        :return: True, если атрибут найден, иначе False.
        """
        return True if key in self.__attributes else False
    
    def __len__ (self) -> int:
        """
        Количество атрибутов.
        :return: Количество атрибутов.
        """
        return len(self.__attributes)
    
    def keys (self) -> list[str]:
        """
        Возвращает список ключей атрибутов.
        :return: Список ключей атрибутов.
        """
        return list(self.__attributes.keys())
    
    def values (self) -> list[str]:
        """
        Возвращает список значений атрибутов.
        :return: Список значений атрибутов.
        """
        return list(self.__attributes.values())