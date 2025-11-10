# anb_python_components/custom_types/two_dim_size.py

class TwoDimSize:
    """
    Класс TwoDimSize для представления размеров двухмерного объекта.
    """
    
    # Разделитель частей по умолчанию.
    DEFAULT_DELIMITER: str = ':'
    
    @staticmethod
    def _get_valid_num (num: int, min_num: int | None = 0, max_num: int | None = None) -> int:
        """
        Получает корректное значение представленного числа.
        :param num: Проверяемое значение.
        :param min_num: Минимальное значение (по умолчанию 0). Если None, то считается, что минимальное значение не ограничено.
        :param max_num: Максимальное значение (по умолчанию None). Если None, то считается, что максимальное значение не ограничено.
        :return: Корректное значение.
        """
        # Флаг, разрешающий или запрещающий отрицательные значения
        is_negative_allowed = min_num < 0 or min_num is None
        
        # Безлимитные значения
        # - для минимального значения
        is_unlimited_min = min_num is None
        # - для максимального значения
        is_unlimited_max = max_num is None
        
        # Если значение отрицательное, а отрицательные значения запрещены
        if num < 0 and not is_negative_allowed:
            # - то возвращаю 0
            return 0
        
        # Если значение вышло за ограничения минимальное значения
        if not is_unlimited_min and num < min_num:
            # - то возвращаю минимальное значение
            return min_num
        
        # Если значение вышло за ограничения максимальное значения
        if not is_unlimited_max and num > max_num:
            # - то возвращаю максимальное значение
            return max_num
        
        # Если значение корректно, то возвращаю его
        return num
    
    def __init__ (
            self, width: int = 0, height: int = 0, min_width: int | None = 0, max_width: int | None = None,
            min_height: int | None = 0, max_height: int | None = None
            ):
        """
        Инициализирует объект TwoDimSize.
        :param width: Ширина (по умолчанию 0).
        :param height: Высота (по умолчанию 0).
        :param min_width: Минимальная ширина (по умолчанию 0). Если None, то считается, что минимальная ширина не ограничена.
        :param max_width: Максимальная ширина (по умолчанию None). Если None, то считается, что максимальная ширина не ограничена.
        :param min_height: Минимальная высота (по умолчанию 0). Если None, то считается, что минимальная высота не ограничена.
        :param max_height: Максимальная высота (по умолчанию None). Если None, то считается, что максимальная высота не ограничена.
        """
        
        # Если некорректно заданы минимальные и максимальные значения ширины
        if min_width is not None and max_width is not None and min_width > max_width:
            # - то выбрасываю исключение
            raise ValueError("Минимальная ширина не может быть больше максимальной.")
        
        # Если некорректно заданы минимальные и максимальные значения высоты
        elif min_height is not None and max_height is not None and min_height > max_height:
            # - то выбрасываю исключение
            raise ValueError("Минимальная высота не может быть больше максимальной.")
        
        # Задаю минимальные и максимальные
        # - для ширины
        # -- минимальное
        self._min_width: int | None = min_width
        # -- максимальное
        self._max_width: int | None = max_width
        # - для высоты
        # -- минимальное
        self._min_height: int | None = min_height
        # -- максимальное
        self._max_height: int | None = max_height
        
        # Устанавливаю ширину
        self._width: int = self._get_valid_num(width, min_width, max_width)
        
        # Устанавливаю высоту
        self._height: int = self._get_valid_num(height, min_height, max_height)
    
    @property
    def min_width (self) -> int:
        """
        Минимальная ширина.
        :return: Значение минимальной ширины.
        """
        return self._min_width
    
    @min_width.setter
    def min_width (self, value: int):
        """
        Устанавливает минимальную ширину и пересчитывает ширину, если она выходит за новые ограничения.
        :param value: Новое значение минимальной ширины.
        :return: None
        """
        # Если максимальная ширина ограничена и значение минимальной ширины больше максимальной ширины,
        # то устанавливаю минимальную ширину равной максимальной ширине, иначе возвращаю значение
        self._min_width = self._max_width if self._max_width is not None and value > self._max_width else value
        
        # При изменении минимальной ширины пересчитываю ширину
        self.width = self._width
    
    @min_width.deleter
    def min_width (self):
        """
        Удаляет минимальную ширину и устанавливает минимальную ширину в 0.
        :return: None
        """
        self._min_width = 0
    
    @property
    def max_width (self) -> int:
        """
        Максимальная ширина.
        :return: Значение максимальной ширины.
        """
        return self._max_width
    
    @max_width.setter
    def max_width (self, value: int):
        """
        Устанавливает максимальную ширину и пересчитывает ширину, если она выходит за новые ограничения.
        :param value: Новое значение максимальной ширины.
        :return: None
        """
        # Если минимальная ширина ограничена и значение максимальной ширины меньше минимальной ширины,
        # то устанавливаю максимальную ширину равной минимальной ширине, иначе возвращаю значение
        self._max_width = self._min_width if self._min_width is not None and value < self._min_width else value
        
        # При изменении максимальной ширины пересчитываю ширину
        self.width = self._width
    
    @max_width.deleter
    def max_width (self):
        """
        Удаляет максимальную ширину.
        :return: None
        """
        self._max_width = None
    
    @property
    def min_height (self) -> int:
        """
        Минимальная высота.
        :return: Значение минимальной высоты.
        """
        return self._min_height
    
    @min_height.setter
    def min_height (self, value: int):
        """
        Устанавливает минимальную высоту и пересчитывает высоту, если она выходит за новые ограничения.
        :param value: Новое значение минимальной высоты.
        :return: None
        """
        # Если максимальная высота ограничена и значение минимальной высоты больше максимальной высоты,
        # то устанавливаю минимальную высоту равной максимальной высоте, иначе возвращаю значение
        self._min_height = self._max_height if self._max_height is not None and value > self._max_height else value
        
        # При изменении минимальной высоты пересчитываю высоту
        self.height = self._height
    
    @min_height.deleter
    def min_height (self):
        """
        Удаляет минимальную высоту и устанавливает минимальную высоту в 0.
        :return: None
        """
        self._min_height = 0
    
    @property
    def max_height (self) -> int:
        """
        Максимальная высота.
        :return: Значение максимальной высоты.
        """
        return self._max_height
    
    @max_height.setter
    def max_height (self, value: int):
        """
        Устанавливает максимальную высоту и пересчитывает высоту, если она выходит за новые ограничения.
        :param value: Новое значение максимальной высоты.
        :return: None
        """
        # Если минимальная высота ограничена и значение максимальной высоты меньше минимальной высоты,
        # то устанавливаю максимальную высоту равной минимальной высоте, иначе возвращаю значение
        self._max_height = self._min_height if self._min_height is not None and value < self._min_height else value
        
        # При изменении максимальной высоты пересчитываю высоту
        self.height = self._height
    
    @max_height.deleter
    def max_height (self):
        """
        Удаляет максимальную высоту.
        :return: None
        """
        self._max_height = None
    
    @property
    def width (self) -> int:
        """
        Ширина.
        :return: Установленная ширина.
        """
        return self._width
    
    @width.setter
    def width (self, value: int):
        """
        Устанавливает ширину.
        :param value: Новое значение ширины.
        :return: None
        """
        self._width = self._get_valid_num(value, self.min_width, self.max_width)
    
    @width.deleter
    def width (self):
        """
        Удаляет ширину.
        :return: None
        """
        self._width = 0 if self._min_width is None else self._min_width
    
    @property
    def height (self) -> int:
        """
        Высота.
        :return: Установленная высота.
        """
        return self._height
    
    @height.setter
    def height (self, value: int):
        """
        Устанавливает высоту.
        :param value: Новое значение высоты.
        :return: None
        """
        self._height = self._get_valid_num(value, self.min_height, self.max_height)
    
    @height.deleter
    def height (self):
        """
        Удаляет высоту.
        :return: None
        """
        self._height = 0 if self._min_height is None else self._min_height
    
    def as_str (self, delimiter: str = DEFAULT_DELIMITER) -> str:
        """
        Возвращает строковое представление объекта TwoDimSize в формате "ширина:высота".
        :param delimiter: Разделитель частей ширины и высоты (по умолчанию ":").
        :return: Строковое представление объекта TwoDimSize.
        """
        return f"{self.width}{delimiter}{self.height}"
    
    def __str__ (self) -> str:
        """
        Строковое представление объекта TwoDimSize.
        :return: Строковое представление объекта TwoDimSize.
        """
        return self.as_str(TwoDimSize.DEFAULT_DELIMITER)
    
    def as_tuple (self) -> tuple[int, int]:
        """
        Возвращает кортеж (ширина, высота).
        :return: Кортеж (ширина, высота).
        """
        return self.width, self.height
    
    def __eq__ (self, other: object) -> bool:
        """
        Сравнивает объект TwoDimSize с другим объектом.
        :param other: Объект для сравнения.
        :return: True, если объекты равны, иначе False.
        """
        # Если сравниваем с объектом TwoDimSize
        if isinstance(other, TwoDimSize):
            # - то сравниваю ширину и высоту
            return self.width == other.width and self.height == other.height
        else:
            # - иначе возвращаю False
            return False
    
    def __repr__ (self) -> str:
        """
        Строковое представление объекта TwoDimSize для отладки.
        :return: Строковое представление объекта TwoDimSize для отладки.
        """
        return f"TwoDimSize({self.width}, {self.height}, min_width={self.min_width}, max_width={self.max_width}, min_height={self.min_height}, max_height={self.max_height})"
    
    def __hash__ (self) -> int:
        """
        Хэш объекта TwoDimSize.
        :return: Хэш объекта TwoDimSize.
        """
        return hash((self.width, self.height))
    
    def __copy__ (self) -> 'TwoDimSize':
        """
        Копирует объект TwoDimSize.
        :return: Копия объекта TwoDimSize.
        """
        return TwoDimSize(self.width, self.height, self.min_width, self.max_width, self.min_height, self.max_height)
    
    def __deepcopy__ (self, memo: dict) -> 'TwoDimSize':
        """
        Глубокое копирование объекта TwoDimSize.
        :param memo: Словарь для хранения копий объектов.
        :return: Глубокая копия объекта TwoDimSize.
        """
        # Если объект уже был скопирован
        if id(self) in memo:
            # - то возвращаю его копию
            return memo[id(self)]
        else:
            # - иначе создаю копию объекта
            memo[id(self)] = copy = TwoDimSize(
                    self.width, self.height, self.min_width, self.max_width, self.min_height, self.max_height
                    )
            # - и возвращаю её
            return copy
    
    def __add__ (self, other: 'TwoDimSize') -> 'TwoDimSize':
        """
        Складывает объект TwoDimSize с другим объектом TwoDimSize.
        :param other: Объект TwoDimSize для сложения.
        :return: Объект TwoDimSize, полученный после сложения.
        """
        # Если другой объект является объектом TwoDimSize
        if isinstance(other, TwoDimSize):
            # - то складываю ширину и высоту с объектом TwoDimSize и возвращаю результат в виде объекта TwoDimSize
            return TwoDimSize(
                    self.width + other.width, self.height + other.height, self.min_width, self.max_width,
                    self.min_height, self.max_height
                    )
        else:
            # - иначе выбрасываю исключение
            raise TypeError("Невозможно сложить два объекта разных типов.")
    
    def __mul__ (self, other: int) -> 'TwoDimSize':
        """
        Умножает объект TwoDimSize на целое число.
        :param other: Целое число для умножения.
        :return: Объект TwoDimSize, полученный после умножения.
        """
        # Если другой объект является целым числом
        if isinstance(other, int):
            # - то перемножаю ширину и высоту на целое число и возвращаю результат в виде объекта TwoDimSize
            return TwoDimSize(
                    self.width * other, self.height * other, self.min_width, self.max_width, self.min_height,
                    self.max_height
                    )
        else:
            # - иначе выбрасываю исключение
            raise TypeError("Невозможно перемножить объект TwoDimSize на другой объект.")
    
    @staticmethod
    def parse (
            text: str, delimiter: str = DEFAULT_DELIMITER, min_width: int | None = 0, max_width: int | None = None,
            min_height: int | None = 0, max_height: int | None = None
            ) -> 'TwoDimSize':
        """
        Создает объект TwoDimSize из строки.
        :param max_height: Минимальная высота (по умолчанию 0). Если None, то считается, что минимальная высота не ограничена.
        :param min_height: Максимальная высота (по умолчанию None). Если None, то считается, что максимальная высота не ограничена.
        :param max_width: Максимальная ширина (по умолчанию None). Если None, то считается, что максимальная ширина не ограничена.
        :param min_width: Минимальная ширина (по умолчанию 0). Если None, то считается, что минимальная ширина не ограничена.
        :param text: Строка для создания объекта TwoDimSize.
        :param delimiter: Разделитель частей ширины и высоты (по умолчанию ":").
        :return: Объект TwoDimSize.
        :raises ValueError: Если строка имеет неверный формат.
        :raises TypeError: При попытке преобразовать строку в объект int (ширину или высоту).
        """
        # Разделяю значения
        split_sizes = text.split(delimiter)
        
        # Проверяю, что массив имеет ровно два элемента
        if len(split_sizes) != 2:
            # - иначе выбрасываю исключение
            raise ValueError("Неверный формат строки для TwoDimSize.")
        
        # Получаю ширину и высоту
        width, height = split_sizes
        
        # Проверяю, что ширина получена
        if width:
            # - и перевожу ее в целое число
            width = int(width)
        else:
            # - иначе выбрасываю исключение
            raise ValueError("Неверный формат ширины  в строке для TwoDimSize.")
        
        # Проверяю, что высота получена
        if height:
            # - и перевожу ее в целое число
            height = int(height)
        else:
            # - иначе выбрасываю исключение
            raise ValueError("Неверный формат высоты в строке для TwoDimSize.")
        
        # Если все проверки пройдены успешно, то создаю объект TwoDimSize с заданными шириной и высотой и возвращаю его
        return TwoDimSize(width, height, min_width, max_width, min_height, max_height)