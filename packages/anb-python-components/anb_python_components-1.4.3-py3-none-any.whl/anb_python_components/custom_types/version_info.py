# anb_python_components/custom_types/version_info.py
import re

from anb_python_components.extensions.string_extension import StringExtension

class VersionInfo:
    """
    Класс для работы с версиями.
    """
    # Шаблон вывода по умолчанию.
    DEFAULT_TEMPLATE: str = '#{Major}.#{Minor}.#{Release}.#{Build} #{Stage} #{StageNumber}'
    
    def __init__ (self, major: int, minor: int, release: int, build: int, stage: str = '', stage_number: int = 0):
        """
        Создание экземпляра класса VersionInfo.
        :param major: Мажорная версия.
        :param minor: Минорная версия.
        :param release: Номер релиза.
        :param build: Номер сборки.
        :param stage: Стадия.
        :param stage_number: Номер стадии.
        """
        self.__major: int = major
        self.__minor: int = minor
        self.__release: int = release
        self.__build: int = build
        self.__stage: str = stage
        self.__stage_number: int = stage_number
    
    # Мажорная версия
    @property
    def major (self) -> int:
        """
        Получение значения major.
        :return: Значение major.
        """
        return self.__major
    
    @major.setter
    def major (self, value: int):
        """
        Установка значения major.
        :param value: Значение major.
        :return: None
        """
        self.__major = value if value >= 0 else 0
    
    @major.deleter
    def major (self):
        """
        Удаление значения major.
        :return: None
        """
        self.__major = 0
    
    # Минорная версия
    @property
    def minor (self) -> int:
        """
        Получение значения minor.
        :return: Значение minor.
        """
        return self.__minor
    
    @minor.setter
    def minor (self, value: int):
        """
        Установка значения minor.
        :param value: Значение minor.
        :return: None
        """
        self.__minor = value if value >= 0 else 0
    
    @minor.deleter
    def minor (self):
        """
        Удаление значения minor.
        :return: None
        """
        self.__minor = 0
    
    # Номер релиза
    @property
    def release (self) -> int:
        """
        Получение значения release.
        :return: Значение release.
        """
        return self.__release
    
    @release.setter
    def release (self, value: int):
        """
        Установка значения release.
        :param value: Значение release.
        :return: None
        """
        self.__release = value if value >= 0 else 0
    
    @release.deleter
    def release (self):
        """
        Удаление значения release.
        :return: None
        """
        self.__release = 0
    
    # Номер сборки
    @property
    def bild (self) -> int:
        """
        Получение значения bild.
        :return: Значение bild.
        """
        return self.__build
    
    @bild.setter
    def bild (self, value: int):
        """
        Установка значения bild.
        :param value: Значение bild.
        :return: None
        """
        self.__build = value if value >= 0 else 0
    
    @bild.deleter
    def bild (self):
        """
        Удаление значения bild.
        :return: None
        """
        self.__build = 0
    
    # Стадия
    @property
    def stage (self) -> str:
        """
        Получение значения stage.
        :return: Значение stage.
        """
        return self.__stage
    
    @stage.setter
    def stage (self, value: str | None):
        """
        Установка значения stage.
        :param value: Значение stage.
        :return: None
        """
        self.__stage = value if value is not None else ''
    
    @stage.deleter
    def stage (self):
        """
        Удаление значения stage.
        :return: None
        """
        self.__stage = ''
    
    # Номер стадии
    @property
    def stage_number (self) -> int:
        """
        Получение значения stage_number.
        :return: Значение stage_number.
        """
        return self.__stage_number
    
    @stage_number.setter
    def stage_number (self, value: int):
        """
        Установка значения stage_number.
        :param value: Значение stage_number.
        :return: None
        """
        self.__stage_number = value if value >= 0 else 0
    
    @stage_number.deleter
    def stage_number (self):
        """
        Удаление значения stage_number.
        :return: None
        """
        self.__stage_number = 0
    
    def to_string (self, template: str = DEFAULT_TEMPLATE) -> str:
        """
        Преобразование экземпляра класса VersionInfo в строку.
        :param template: Шаблон для преобразования.
        :return: Строка с версией.
        """
        # Создание словаря для замены
        template_dict = {
                '#{Major}': str(self.major),
                '#{Minor}': str(self.minor),
                '#{Release}': str(self.release),
                '#{Build}': str(self.bild),
                '#{Stage}': str(self.stage),
                '#{StageNumber}': str(self.stage_number) if self.stage_number > 0 else ''
                }
        
        # Замена значений в шаблоне
        replaced = StringExtension.replace_all(template_dict, template)
        
        # Удаление лишних пробелов и символов в начале и конце строки и возврат результата
        return replaced.strip()
    
    def __str__ (self) -> str:
        """
        Переопределение метода __str__.
        :return: Строка с версией.
        """
        return self.to_string(VersionInfo.DEFAULT_TEMPLATE)
    
    def __repr__ (self) -> str:
        """
        Переопределение метода __repr__.
        :return: Строка с версией.
        """
        return f'VersionInfo(major={self.major}, minor={self.minor}, release={self.release}, build={self.bild}, stage={self.stage}, stage_number={self.stage_number})'
    
    def __compare (self, other: 'VersionInfo') -> int:
        """
        Сравнение версий.
        :param other: Версия для сравнения.
        :return: 1, если текущая версия больше, -1, если текущая версия меньше, 0, если версии равны.
        """
        # Проверка типа
        if not isinstance(other, VersionInfo):
            # - если other не является экземпляром VersionInfo, то выбрасываем исключение
            raise TypeError(f'Невозможно сравнить тип VersionInfo с {type(other)}')
        
        # Сравнение мажорных версий. Если текущая мажорная версия больше
        if self.major > other.major:
            # - возвращаем 1
            return 1
        # Если текущая мажорная версия меньше
        elif self.major < other.major:
            # - возвращаем -1
            return -1
        
        # Если мажорные версии равны, то сравниваем минорные версии. Если текущая минорная версия больше
        if self.minor > other.minor:
            # - возвращаем 1
            return 1
        # Если текущая минорная версия меньше
        elif self.minor < other.minor:
            # - возвращаем -1
            return -1
        
        # Если мажорные и минорные версии равны, то сравниваем номер релиза. Если текущий номер релиза больше
        if self.release > other.release:
            # - возвращаем 1
            return 1
        # Если текущий номер релиза меньше
        elif self.release < other.release:
            # - возвращаем -1
            return -1
        
        # Если мажорные, минорные и номер релиза равны, то сравниваем номер сборки. Если текущий номер сборки больше
        if self.bild > other.bild:
            # - возвращаем 1
            return 1
        # Если текущий номер сборки меньше
        elif self.bild < other.bild:
            # - возвращаем -1
            return -1
        
        # Если мажорные, минорные, номер релиза и номер сборки равны, то равны и версии. Возвращаем 0.
        return 0
    
    def __eq__ (self, other: 'VersionInfo') -> bool:
        """
        Сравнение версий на равенство (==).
        :param other: Версия для сравнения.
        :return: True, если версии равны, False, если версии не равны.
        """
        # Проверка типа
        if not isinstance(other, VersionInfo):
            # - если other не является экземпляром VersionInfo, то выбрасываем исключение
            raise TypeError(f'Невозможно сравнить тип VersionInfo с {type(other)}')
        
        # Если версии равны, то возвращаем True
        return self.__compare(other) == 0
    
    def __ne__ (self, other: 'VersionInfo') -> bool:
        """
        Сравнение версий на неравенство (!=).
        :param other: Версия для сравнения.
        :return: True, если версии не равны, False, если версии равны.
        """
        # Проверка типа
        if not isinstance(other, VersionInfo):
            # - если other не является экземпляром VersionInfo, то выбрасываем исключение
            raise TypeError(f'Невозможно сравнить тип VersionInfo с {type(other)}')
        
        # Если версии не равны, то возвращаем True
        return self.__compare(other) != 0
    
    def __lt__ (self, other: 'VersionInfo') -> bool:
        """
        Сравнение версий на меньше (<).
        :param other: Версия для сравнения.
        :return: True, если текущая версия меньше, False, если текущая версия больше или равна.
        """
        # Проверка типа
        if not isinstance(other, VersionInfo):
            # - если other не является экземпляром VersionInfo, то выбрасываем исключение
            raise TypeError(f'Невозможно сравнить тип VersionInfo с {type(other)}')
        
        # Если текущая версия меньше, то возвращаем True
        return self.__compare(other) == -1
    
    def __gt__ (self, other: 'VersionInfo') -> bool:
        """
        Сравнение версий на больше (>).
        :param other: Версия для сравнения.
        :return: True, если текущая версия больше, False, если текущая версия меньше или равна.
        """
        # Проверка типа
        if not isinstance(other, VersionInfo):
            # - если other не является экземпляром VersionInfo, то выбрасываем исключение
            raise TypeError(f'Невозможно сравнить тип VersionInfo с {type(other)}')
        
        # Если текущая версия больше, то возвращаем True
        return self.__compare(other) == 1
    
    def __le__ (self, other: 'VersionInfo') -> bool:
        """
        Сравнение версий на меньше или равно (<=).
        :param other: Версия для сравнения.
        :return: True, если текущая версия меньше или равна, False, если текущая версия больше.
        """
        # Проверка типа
        if not isinstance(other, VersionInfo):
            # - если other не является экземпляром VersionInfo, то выбрасываем исключение
            raise TypeError(f'Невозможно сравнить тип VersionInfo с {type(other)}')
        
        # Если текущая версия меньше или равна, то возвращаем True
        return self.__compare(other) in (0, -1)
    
    def __ge__ (self, other: 'VersionInfo') -> bool:
        """
        Сравнение версий на больше или равно (>=).
        :param other: Версия для сравнения.
        :return: True, если текущая версия больше или равна, False, если текущая версия меньше.
        """
        # Проверка типа
        if not isinstance(other, VersionInfo):
            # - если other не является экземпляром VersionInfo, то выбрасываем исключение
            raise TypeError(f'Невозможно сравнить тип VersionInfo с {type(other)}')
        
        # Если текущая версия больше или равна, то возвращаем True
        return self.__compare(other) in (0, 1)
    
    def in_range (
            self, start: 'VersionInfo' or None = None, end: 'VersionInfo' or None = None, start_inclusive: bool = True,
            end_inclusive: bool = True
            ) -> bool:
        """
        Проверка версии на принадлежность диапазону.
        :param start: Начало диапазона (по умолчанию None). Если start равен None, то считается, что start не ограничен.
        :param end: Конец диапазона (по умолчанию None). Если end равен None, то считается, что end не ограничен.
        :param start_inclusive: Включать ли начало диапазона (по умолчанию True).
        :param end_inclusive: Включать ли конец диапазона (по умолчанию True).
        :return: True, если версия принадлежит диапазону, False, если версия не принадлежит диапазону.
        """
        # Если start не указан
        if start is None:
            # - устанавливаем start_inclusive равным True
            start_inclusive = True
            # - устанавливаем start равным self
            start = self
        
        # Если end не указан
        if end is None:
            # - устанавливаем end_inclusive равным True
            end_inclusive = True
            # - устанавливаем end равным self
            end = self
        
        # Проверка типов
        if not isinstance(start, VersionInfo) or not isinstance(end, VersionInfo):
            # - если start или end не являются экземплярами VersionInfo, то выбрасываем исключение
            raise TypeError(f'Невозможно сравнить тип VersionInfo с {type(start)} и {type(end)}')
        
        # Если start совпадает с версией
        if self == start:
            # - если включать начало диапазона (start_inclusive), то возвращаем True, иначе False
            return True if start_inclusive else False
        
        # Если end совпадает с версией
        if self == end:
            # - если включать конец диапазона (end_inclusive), то возвращаем True, иначе False
            return True if end_inclusive else False
        
        # Если текущая версия находится между start и end, то возвращаем True, иначе False
        return True if start < self < end else False
    
    @staticmethod
    def parse (version: str) -> 'VersionInfo':
        version = version.strip()
        
        # Разбиваем строку на части по пробелам (1 часть - основная - мажор, минор, релиз, сборка,
        # 2 часть - стадия и 3 - номер стадии):
        # - находим позицию первого пробела
        start = version.find(" ")
        # - если позиция первого пробела не найдена
        if start == -1:
            # - устанавливаем конец строки
            start = len(version)
        # - находим позицию последнего пробела
        end = version.rfind(" ") if start < len(version) else -1
        
        # - получаем основную часть
        main_part = version[:start].strip()
        # - получаем стадию
        stage = version[start:end].strip() if end > 0 else ''
        # - получаем номер стадии в виде строки
        stage_number_text = version[end:].strip()
        # - получаем номер стадии из строки
        try:
            stage_number = int(stage_number_text)
        except ValueError:
            stage_number = 0
        
        # Составляем регулярное выражение для парсинга базовой информации о версии
        pattern = r'^(\d+)(?:\.(\d+))?(?:\.(\d+))?(?:\.(\d+))?$'
        
        # Парсим базовую информацию о версии
        matches = re.match(pattern, main_part)
        
        # Если не удалось найти соответствие
        if not matches:
            # - возвращаем пустую версию
            return VersionInfo(0, 0, 0, 0, stage, stage_number)
        
        # Получаем группы из совпадения
        groups = matches.groups()
        
        # Проверяем, что найдены как минимум 2 части
        if len(groups) < 2:
            # - иначе возвращаем пустую версию
            return VersionInfo(0, 0, 0, 0, stage, stage_number)
        
        # Проверяем, что групп 4
        if len(groups) != 4:
            # - иначе возвращаем пустую версию
            return VersionInfo(0, 0, 0, 0, stage, stage_number)
        
        # Распаковываем значения
        major, minor, release, build = groups
        
        # Преобразуем строки в целые числа
        major = int(major) if major else 0
        minor = int(minor) if minor else 0
        release = int(release) if release else 0
        build = int(build) if build else 0
        
        # Возвращаем экземпляр класса VersionInfo с полученными значениями
        return VersionInfo(major, minor, release, build, stage, stage_number)