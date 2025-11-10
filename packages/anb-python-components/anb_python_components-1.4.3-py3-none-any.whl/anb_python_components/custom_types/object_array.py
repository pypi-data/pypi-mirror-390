# anb_python_components/custom_types/object_array.py
from __future__ import annotations

import copy
import inspect
import time
from typing import Any, Callable, get_args, get_type_hints

from anb_python_components.enums.type_copy_strategy import TypeCopyStrategy
from anb_python_components.extensions.type_extension import TypeExtension

# noinspection Annotator
class ObjectArray[T]:
    """
    Класс для хранения массива объектов.
    """
    
    # Добавление слотов для хранения массива
    __slots__ = [
            '__container', '_cache', '_cache_ttl', '_max_cache_size',
            '_cache_hits', '_cache_misses', '__default_cache_ttl'
            ]
    
    def __init__ (
            self, array: list[T] | None = None, copy_strategy: TypeCopyStrategy = TypeCopyStrategy.AUTO,
            cache_size: int = 100, cache_default_ttl: int = 3600
            ):
        """
        Инициализация массива объектов.
        :param array: Список объектов или None.
        :param copy_strategy: Стратегия копирования массива. По умолчанию AUTO.
        :param cache_size: Максимальный размер кэша. По умолчанию 100.
        :param cache_default_ttl: Время жизни кэша по умолчанию в секундах. По умолчанию 3600.
        """
        # Проверка входных данных
        if array is not None:
            # - если не массив
            if not isinstance(array, list):
                # -- то выбрасываем исключение
                raise TypeError("Переменная array должна быть типа list / Array must be a list")
        
        # Активация системы кэширования
        # - словарь для хранения кэша
        self._cache = {}
        # - время жизни кэша
        self._cache_ttl = {}
        # - максимальный размер кэша
        self._max_cache_size = cache_size
        # - счетчик попаданий в кэш
        self._cache_hits = 0
        # - счетчик промахов
        self._cache_misses = 0
        # - время жизни кэша по умолчанию
        self.__default_cache_ttl = cache_default_ttl
        
        # Копирование массива по стратегии
        if copy_strategy == TypeCopyStrategy.IGNORE:
            self.__container = array
        elif copy_strategy == TypeCopyStrategy.COPY:
            self.__container = array.copy()
        elif copy_strategy == TypeCopyStrategy.DEEP_COPY:
            self.__container = copy.deepcopy(array)
        else:
            t_type = get_args(get_type_hints(self.__class__).get('T'))
            # noinspection PyTypeChecker
            self.__container = copy.deepcopy(array) if not TypeExtension.is_immutable_type(t_type) else array.copy()
    
    def __iter__ (self):
        """
        Итератор.
        :return: Итератор.
        :rtype: Iterator[T]
        """
        return iter(self.__container)
    
    def __getitem__ (self, key: int) -> T | None:
        """
        Доступ к атрибутам по ключу.
       :param key: Ключ атрибута.
        :type key: int
        :return: Значение атрибута или None, если атрибут не найден.
        :rtype: T | None
        """
        # Если ключ отрицательный или больше или равен длине массива
        if key < 0 or key >= len(self.__container):
            # - то возвращаем None
            return None
        
        # Возвращаем значение
        return self.__container[key]
    
    def __setitem__ (self, key: int, value: T) -> None:
        """
        Установить значение атрибута.
        :param key: Ключ атрибута.
        :type key: int
        :param value: Значение атрибута.
        :type value: T
        :return: None
        """
        self.__container[key] = value
    
    def __contains__ (self, item: T) -> bool:
        """
        Проверка наличия элемента в массиве.
        :param item: Проверяемый элемент.
        :type item: T
        :return: True, если элемент найден, False, если элемент не найден.
        """
        return self.is_exists(lambda elem: elem == item)
    
    def __len__ (self) -> int:
        """
        Количество атрибутов.
        :return: Количество атрибутов.
        :rtype: int
       """
        return self.count()
    
    @staticmethod
    def default_compare () -> Callable[[T, T], bool]:
        """
        Статический метод для получения функции сравнения по умолчанию.
        :return: Функция сравнения по умолчанию.
        :rtype: Callable[[T, T], bool]
        """
        return lambda x, y: x == y
    
    ### Специальные методы ###
    def clear (self) -> None:
        """
        Очистка массива.
        """
        # Очищаем массив
        self.__container.clear()
        # Очищаем кэш
        self._cache.clear()
    
    def add (self, value: T) -> None:
        """
        Добавление значения в массив.
        :param value: Значение.
        :type value: T
        """
        # Если значения нет в массиве
        if value not in self.__container:
            # - то добавляем
            self.__container.append(value)
            # - и очищаем кэш
            self._cache.clear()
    
    def add_range (self, values: list[T] | ObjectArray[T]) -> None:
        """
        Добавление диапазона значений в массив.
        :param values: Значения, которые нужно добавить. Можно передавать массив или объект класса ObjectArray.
        :type values: list[T] | ObjectArray[T]
        """
        # Если передан массив, то не изменяем его, а если передан объект класса ObjectArray, то конвертируем его в массив объектов
        object_array = values.to_array() if isinstance(values, ObjectArray) else values
        
        # Если значения есть
        if len(object_array) > 0:
            # - то добавляем их
            self.__container += object_array
            # - и очищаем кэш
            self._cache.clear()
    
    def to_array (self) -> list[T]:
        """
        Получение массива.
        :return: Массив.
        :rtype: list[T]
        """
        # Если массив не пустой
        if len(self.__container) > 0:
            # - то возвращаем его
            return self.__container
        else:
            # - иначе возвращаем пустой массив
            return []
    
    ### Поиск и сортировка ###
    def find (self, value: Any, compare: Callable[[T, Any], bool] = default_compare()) -> T | None:
        """
        Поиск значения в массиве.
        :param value: Значение, которое нужно найти.
        :type value: Any
        :param compare: Функция сравнения.
        :type value: Callable[[T, Any], bool]
        :return: Найденное значение или None.
        :rtype: T | None
        """
        
        # Для каждого элемента массива
        for item in self.__container:
            # - выполняем сравнение по функции сравнения
            if compare(item, value):
                # -- и возвращаем элемент, если он найден
                return item
        
        # Если мы сюда дошли, значить объект не найден - возвращаем None
        return None
    
    def sort (self, object_property: str, descending: bool = False) -> None:
        """
        Сортирует контейнер объектов по указанному атрибуту.
    
        :param object_property: Имя атрибута объекта для сортировки
        :type object_property: str
        :param descending: если True — сортировка по убыванию
        :type descending: bool
        """
        try:
            # Сортируем массив объектов
            self.__container.sort(key = lambda obj: getattr(obj, object_property), reverse = descending)
        except AttributeError:
            # Если атрибут не найден, выбрасываем исключение
            raise ValueError(f"Свойство {object_property} / Property {object_property} not found")
    
    def sort_callback (
            self,
            predicate: Callable[[T], Any],
            descending: bool = False
            ) -> None:
        """
        Сортирует контейнер, используя пользовательскую функцию-предикат.
    
        :param predicate: Функция, принимающая объект и возвращающая значение свойства для сравнения.
        :type predicate: Callable[[T], Any]
        :param descending: если True — сортировка по убыванию.
        :type descending: bool
        """
        self.__container.sort(
                key = predicate,
                reverse = descending
                )
    
    ### Операторы LINQ ###
    ### 1. Операторы проверки существования и количества ###
    def count (self, where: Callable[[T], bool] = None) -> int:
        """
        Количество элементов в массиве.
        :param where: Функция выборки элементов. Вместо неё можно передать None, тогда будут возвращено общее
            количество объектов в массиве. По умолчанию, None.
        :type where: Callable[[T], bool] | None
        :return: Количество элементов.
        :rtype: int
        """
        # Формируем ключ кэша
        cache_key = self._generate_cache_key('count', where)
        
        # Проверяем кэш на наличие ключа и его актуальность и если он есть
        if self._in_cache(cache_key):
            # - получаем из кэша
            return self._get_from_cache(cache_key)
        
        # Если массив пустой
        if not self.__container:
            # - то кэшируем 0
            self._set_to_cache(cache_key, 0)
            # - и возвращаем 0
            return 0
        
        # Вычисляем результат
        result = sum(1 for item in self.__container if where(item)) if where else len(self.__container)
        
        # Кэшируем результат
        self._set_to_cache(cache_key, result)
        
        # Возвращаем результат
        return result
    
    def is_exists (self, where: Callable[[T], bool]) -> bool:
        """
        Проверка наличия элементов в массиве.
        :param where: Функция выборки элементов.
        :type where: Callable[[T], bool]
        :return: True, если есть хотя бы один элемент, удовлетворяющий условию, иначе False.
        :rtype: bool
        """
        return self.count(where) > 0
    
    ### 2. Операторы выбора минимума и максимума ###
    def min (self, by_value: Callable[[T], Any]) -> T | None:
        """
        Минимальное значение.
        :param by_value: Функция, возвращающая значение для сравнения.
        :type by_value: Callable[[T], Any]
        :return: Минимальное значение или None.
        :rtype: T | None
        """
        # Задаём ключ кэша
        cache_key = self._generate_cache_key('min', by_value)
        
        # Если есть кэш
        if self._in_cache(cache_key):
            # - возвращаем его
            return self._get_from_cache(cache_key)
        
        # Если массив пустой
        if not self.__container:
            # - то кэшируем None
            self._set_to_cache(cache_key, None)
            # - и возвращаем None
            return None
        
        # Возвращаем минимальное значение
        result = min(
                self.__container,
                key = by_value
                )
        
        # Кэшируем результат
        self._set_to_cache(cache_key, result)
        
        # Возвращаем результат
        return result
    
    def max (self, by_value: Callable[[T], Any]) -> T | None:
        """
        Максимальное значение.
        :param by_value: Функция, возвращающая значение для сравнения.
        :type by_value: Callable[[T], Any]
        :return: Максимальное значение или None.
        :rtype: T | None
        """
        # Задаём ключ кэша
        cache_key = self._generate_cache_key('max', by_value)
        
        # Если есть кэш
        if self._in_cache(cache_key):
            # - возвращаем его
            return self._get_from_cache(cache_key)
        
        # Если массив пустой
        if not self.__container:
            # - то кэшируем None
            self._set_to_cache(cache_key, None)
            # - и возвращаем None
            return None
        
        # Возвращаем максимальное значение
        result = max(
                self.__container,
                key = by_value
                )
        
        # Кэшируем результат
        self._set_to_cache(cache_key, result)
        
        # Возвращаем результат
        return result
    
    ### 3. Операторы выбора элементов ###
    def get_rows (self, where: Callable[[T], bool] = None) -> ObjectArray[T]:
        """
        Выделяет из массива объектов объекты, удовлетворяющие условию.
        :param where: Функция выборки объектов. Вместо неё можно передать None, тогда будут возвращены все объекты.
            По умолчанию, None.
        :type where: Callable[[T], bool] | None
        :return: Массив объектов, удовлетворяющих условию.
        :rtype: ObjectArray[T]
        """
        # Задаём ключ кэша
        cache_key = self._generate_cache_key('get_rows', where)
        
        # Если есть кэш
        if self._in_cache(cache_key):
            # - возвращаем его
            return self._get_from_cache(cache_key)
        
        # Если функция выборки не задана или массив пустой
        if where is None or not self.__container:
            # - то просто копируем массив
            return ObjectArray(self.__container)
        
        # Выбираем элементы, удовлетворяющие условию и создаём новый массив
        items = ObjectArray([item for item in self.__container if where(item)])
        
        # Кэшируем результат
        self._set_to_cache(cache_key, items)
        
        # Возвращаем результат
        return items
    
    def get_row (self, where: Callable[[T], bool] = None) -> T | None:
        """
        Выбирает из массива объектов объект, удовлетворяющий условию.
        :param where: Функция выборки объектов. Вместо неё можно передать None, тогда будет возвращён первый объект.
            По умолчанию, None.
        :type where: Callable[[T], bool] | None
        :return: Объект, удовлетворяющий условию или None, если объект не найден.
        :rtype: T | None
        """
        # Если массив пустой
        if not self.__container:
            # - то возвращаем None
            return None
        
        # Если функция выборки не задана
        if where is None:
            # - то возвращаем первый элемент
            return self.__container[0]
        
        # Выбираем элементы, удовлетворяющие условию
        rows: ObjectArray[T] = self.get_rows(where)
        
        # Если элементов не найдено
        if len(rows) == 0:
            # - то возвращаем None
            return None
        
        # Возвращаем первый найденный элемент
        return rows[0]
    
    def where (self, where: Callable[[T], bool]) -> ObjectArray[T]:
        """
        Выбирает из массива объектов объекты, удовлетворяющие условию.
        :param where: Функция выборки объектов.
        :type where: Callable[[T], bool]
        :return: Массив объектов, удовлетворяющих условию, если объектов несколько, или объект, удовлетворяющий условию,
            если объект единственный, или None, если объект не найден.
        :rtype: T | ObjectArray[T] | None
        """
        # Задаём ключ кэша
        cache_key = self._generate_cache_key('where', where)
        
        # Если есть кэш
        if self._in_cache(cache_key):
            # - возвращаем его
            return self._get_from_cache(cache_key)
        
        # Выбираем элементы, удовлетворяющие условию
        result = ObjectArray([item for item in self.__container if where(item)])
        
        # Кэшируем результат
        self._set_to_cache(cache_key, result)
        
        # Возвращаем результат
        return result
    
    def get_column (self, column_name: str, where: Callable[[T], bool] = None) -> ObjectArray[Any]:
        """
        Выбирает из массива объектов значения свойства.
        :param column_name: Имя свойства.
        :type column_name: str
        :param where: Функция выборки объектов. По умолчанию, None. Если None, то возвращаются свойства всех объектов.
        :type where: Callable[[T], bool] | None
        :return: Массив значений свойства.
        :rtype: ObjectArray[Any]
        """
        return self.get_column_callback(
                lambda item: getattr(item, column_name, None) if hasattr(item, column_name) else None,
                where
                )
    
    def get_column_callback (self, column: Callable[[T], Any], where: Callable[[T], bool] = None) -> ObjectArray[Any]:
        """
        Выбирает из массива объектов значения свойства.
        :param column: Функция получения значения свойства.
        :type column: Callable[[T], Any]
        :param where: Функция выборки объектов. По умолчанию, None. Если None, то возвращаются все объекты.
        :type where: Callable[[T], bool] | None
        :return: Массив значений свойства.
        :rtype: ObjectArray[Any]
        """
        # Задаём ключ кэша
        cache_key = self._generate_cache_key('get_column', [column, where])
        
        # Если есть кэш
        if self._in_cache(cache_key):
            # - возвращаем его
            return self._get_from_cache(cache_key)
        
        # Получаем массив объектов, удовлетворяющих условию
        items = ObjectArray([column(item) for item in self.__container if where is None or where(item)])
        
        # Кэшируем результат
        self._set_to_cache(cache_key, items)
        
        # Возвращаем массив
        return items
    
    def get_value (self, column: str, where: Callable[[T], bool] = None) -> Any | None:
        """
        Получение значение единичного поля. Если полей по выборке будет больше одного, то вернёт первое из них.
        :param column: Требуемый столбец.
        :type column: str
        :param where:Условие выборки., которое проверяет, подходит элемент или нет. Можно передать None, тогда будет
            пробран весь массив. По умолчанию, None.
        :type where: Callable[[T], bool] | None
        :return: Значение поля или None, если поля нет.
        :rtype: Any | None
        """
        # Задаём ключ кэша
        cache_key = self._generate_cache_key(f'get_value_for_{column}', where)
        
        # Если есть кэш
        if self._in_cache(cache_key):
            # - возвращаем его
            return self._get_from_cache(cache_key)
        
        # Получаю колонку
        result = self.get_column(column, where)
        
        # Если колонка пустая
        if len(result) == 0:
            # -- сохраняем None в кэш
            self._set_to_cache(cache_key, None)
            # -- и возвращаем его
            return None
        
        # Получаю первый элемент колонки
        result = result[0]
        
        # Кэширую результат
        self._set_to_cache(cache_key, result)
        
        # Возвращаю результат
        return result
    
    ### 4. Операторы удаления ###
    def delete (self, where: Callable[[T], bool] = None) -> bool:
        """
        Удаление элементов из массива.
        :param where: Функция выборки элементов. По умолчанию, None. Если None, то будут удалены все элементы.
        :type where: Callable[[T], bool] | None
        :return: True, если удаление успешно, False, если удаление не удалось.
        :rtype: bool
        """
        # Если функция выборки не задана
        if where is None:
            # - то очищаем массив
            self.clear()
            # - и прерываем функцию
            return True
        
        # Удаляем элементы, удовлетворяющие условию
        self.__container = [item for item in self.__container if not where(item)]
        
        # Очищаем кэш
        self._cache.clear()
        
        # Возвращаем True
        return True
    
    ### 5. Операторы получения ###
    def first (self, default: T | None = None) -> T | None:
        """
        Безопасное получение первого элемента массива.
        :param default: Значение по умолчанию или None. По умолчанию, None.
        :return: Первый элемент массива, значение по умолчанию или None.
        :rtype: T | None
        """
        return self.__container[0] if self.__container else default
    
    def last (self, default: T | None = None) -> T | None:
        """
        Безопасное получение последнего элемента массива.
        :param default: Значение по умолчанию или None. По умолчанию, None.
        :return: Последний элемент массива, значение по умолчанию или None.
        :rtype: T | None
        """
        return self.__container[-1] if self.__container else default
    
    def skip (self, count: int) -> ObjectArray[T]:
        """
        Пропускает первые count элементов в массиве.
        :param count: Количество пропускаемых элементов.
        :type count: int
        :return: Массив без первых count элементов.
        :rtype: ObjectArray[T]
        """
        # Если требуется пропустить отрицательное количество элементов или нуль
        if count <= 0:
            # - то просто копируем массив
            return ObjectArray(self.__container)
        
        # Если требуется пропустить больше элементов, чем есть в массиве
        if count >= len(self.__container):
            # - то возвращаем пустой массив
            return ObjectArray()
        
        # Возвращаем массив без первых count элементов
        return ObjectArray(self.__container[count:], TypeCopyStrategy.IGNORE)
    
    def take (self, count: int) -> ObjectArray[T]:
        """
        Возвращает первые count элементов в массиве.
        :param count: Количество возвращаемых элементов.
        :type count: int
        :return: Массив с первыми count элементами.
        :rtype: ObjectArray[T]
        """
        # Если требуется взять отрицательное количество элементов или нуль
        if count <= 0:
            # - то возвращаем пустой массив
            return ObjectArray()
        
        # Если требуется взять больше элементов, чем есть в массиве
        if count >= len(self.__container):
            # - то просто копируем массив
            return ObjectArray(self.__container)
        
        # Возвращаем массив с первыми count элементами
        return ObjectArray(self.__container[:count], TypeCopyStrategy.IGNORE)
    
    def skip_and_take (self, skip_count: int, take_count: int) -> ObjectArray[T]:
        """
        Пропускает skip_count элементов и возвращает take_count элементов.
        :param skip_count: Количество пропускаемых элементов.
        :type skip_count: int
        :param take_count: Количество возвращаемых элементов.
        :type skip_count: int
        :return: Массив с пропущенными skip_count элементами и take_count элементами.
        :rtype: ObjectArray[T]
        """
        # Если требуется пропустить отрицательное количество элементов
        if skip_count < 0:
            # - то приравниваем skip_count к нулю
            skip_count = 0
        
        # Если требуется взять отрицательное количество элементов
        if take_count <= 0:
            # - то возвращаем пустой массив
            return ObjectArray([])
        
        # Задаём начало
        start = skip_count
        # Задаём конец - начало + количество элементов, которые нужно взять
        end = start + take_count
        
        # Если начало больше длины массива
        if start >= len(self.__container):
            # - то возвращаем пустой массив
            return ObjectArray([])
        
        # Если конец больше длины массива
        if end >= len(self.__container):
            # - то обрезаем массив до конца
            end = len(self.__container)
        
        # Делаем обрезку массива по началу и концу и возвращаем результат
        return ObjectArray(self.__container[start:end], TypeCopyStrategy.IGNORE)
    
    ## Работа с кэшем ##
    def _get_from_cache (self, key: str) -> Any | None:
        """
        Получение значения из кэша.
        :param key: Ключ.
        :return: Значение или None, если значение не найдено.
        """
        # Если ключ в кэше
        if key in self._cache:
            # - то проверяем время жизни
            if self._cache_ttl[key] > time.time():
                # -- и указываем, что значение есть в кэше, если время ещё не истекло
                self._cache_hits += 1
                
                # -- возвращаем значение из кэша
                return self._cache[key]
            else:
                # -- удаляем просроченное значение из кэша
                del self._cache[key]
                # -- и время жизни
                del self._cache_ttl[key]
        
        # Ключа нет в кэше - промах
        self._cache_misses += 1
        
        # Возвращаем None
        return None
    
    def _set_to_cache (self, key: str, value: Any, ttl: int | None = None) -> None:
        """
        Запись значения в кэш.
        :param key: Ключ.
        :param value: Значение.
        :param ttl: Время жизни в секундах. По умолчанию, self.__default_cache_ttl.
        :return: None.
        """
        # Если время жизни не задано
        if ttl is None:
            # - то берём из настроек класса
            ttl = self.__default_cache_ttl
        
        # Если кэш переполнен
        if len(self._cache) >= self._max_cache_size:
            # - то очищаем кэш
            self._clear_cache()
        
        # Записываем значение в кэш
        self._cache[key] = value
        # - и его время жизни
        self._cache_ttl[key] = time.time() + ttl
    
    def _clear_cache (self) -> None:
        """
        Очищает кэш.
        :return: None.
        """
        # Очищаем кэш
        self._cache.clear()
        # - и время жизни
        self._cache_ttl.clear()
        # - и счётчик попаданий
        self._cache_hits = 0
        # - и счётчик промахов
        self._cache_misses = 0
    
    def cache_stats (self) -> dict:
        """
        Получение статистики по кэшу.
        :return: Статистика по кэшу.
        """
        return {
                "hits": self._cache_hits,
                "misses": self._cache_misses,
                "max_size": self._max_cache_size,
                "size": len(self._cache),
                "hit_ratio": self._cache_hits / (
                        self._cache_hits + self._cache_misses) if self._cache_hits + self._cache_misses > 0 else 0,
                "default_ttl": self.__default_cache_ttl
                }
    
    @staticmethod
    def _generate_cache_key (
            method_name: str, predicates: list[Callable[[T], Any] | None] | Callable[[T], Any] | None = None
            ) -> str:
        # Задаём базовый ключ кэша
        key = method_name
        
        # Если есть предикат
        if predicates:
            # - если это простой предикат
            if not isinstance(predicates, list):
                # -- то оборачиваем его в список
                predicates = [predicates]
            
            # - пробегаем по списку предикатов
            for predicate in predicates:
                # -- если предикат не None
                if predicate:
                    # noinspection PyBroadException
                    try:
                        # --- получаем код функции
                        predicate_code = inspect.getsource(predicate)
                    except:
                        # --- если не получилось, то просто берём его строковое представление
                        predicate_code = str(predicates)
                    
                    # --- и добавляем его код к ключу кэша
                    key += f"_{hash(predicate_code)}"
        
        # Возвращаем ключ кэша
        return key
    
    def _in_cache (self, key: str) -> bool:
        """
        Проверяет, есть ли значение в кэше по ключу и не истёк ли срок его жизни. Если истёк, то удаляет его из кэша.
        :param key: Ключ.
        :return: True, если значение есть в кэше и не истёк срок его жизни, False иначе.
        """
        # Проверяем, есть ли ключ в кэше
        if not key in self._cache:
            # - если нет, то возвращаем провал
            return False
        
        # Если ключ есть в кэше и время жизни не истекло
        if self._cache_ttl[key] > time.time():
            # - возвращаем успех
            return True
        else:
            # - то удаляем просроченное значение из кэша
            del self._cache[key]
            # - и время жизни
            del self._cache_ttl[key]
            # - и возвращаем провал
            return False