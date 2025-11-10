# anb_python_components/classes/action_state.py
import glob
import hashlib
import math
import os

from anb_python_components.classes.action_state import ActionState

class File:
    """
    Класс для работы с файлами.
    """
    
    # Словарь сообщений об ошибках для получения размера файла
    FILE_SIZE_ERROR_MESSAGES: dict[str, str] = {
            'file_not_exist': 'Файл не существует!',
            'not_a_file': 'Указанный путь не является файлом!',
            'cannot_get_size': 'Не удалось получить размер файла!'
            }
    
    # Словарь локализации размеров файлов.
    FILE_SIZE_UNITS: list[str] = ['байт', 'КБ', 'МБ', 'ГБ', 'ТБ']
    
    @staticmethod
    def is_exist (file_path: str) -> bool:
        """
        Проверяет, существует ли файл по указанному пути.
        :param file_path: Путь к файлу.
        :return: bool: True, если файл существует, False в противном случае.
        """
        return True if os.path.exists(file_path) and os.path.isfile(file_path) else False
    
    @staticmethod
    def find (directory: str, pattern: str = '*', exclude_list: set[str] = str()) -> list | bool:
        """
        Ищет файлы, удовлетворяющие заданному паттерну, рекурсивно проходя по указанным директориям.
        :param directory: Директория, в которой производится поиск.
        :param pattern: Маска файла (по умолчанию '*').
        :param exclude_list: Список директорий, которые нужно исключить из итогового списка. Внимание: будут исключены все поддиректории этих директорий.
        :return: list|bool: Список найденных файлов или False, если произошла ошибка.
        """
        try:
            # Начальная точка поиска — указанный каталог
            files = []
            
            # Начинаем обход каталога и его вложенных подкаталогов
            for root, dirs, filenames in os.walk(directory):
                # - фильтруем директории, исключая заданные в exclude_list
                dirs[:] = [d for d in dirs if d not in exclude_list]
                
                # Применяем маску поиска (* или любую другую)
                matches = glob.glob(os.path.join(root, pattern))
                
                # Добавляем найденные файлы в общий список
                files.extend(matches)
            
            # Возвращаем список найденных файлов
            return files
        
        except OSError:
            # Если возникает ошибка файловой операции, возвращаем False
            return False
    
    @staticmethod
    def extract_file_name (file_path: str) -> str:
        """
        Извлекает имя файла из полного пути к нему.
        :param file_path: Полный путь к файлу.
        :return: str: Имя файла.
        """
        return os.path.basename(file_path)
    
    @staticmethod
    def extract_file_extension (file_path: str, with_dot: bool = True) -> str:
        """
        Извлекает расширение файла из полного пути к нему.
        :param file_path: Полный путь к файлу.
        :param with_dot: Если True, точка перед расширением будет добавлена к результату, если False, точка будет удалена.
        :return: str: Расширение файла.
        """
        # Получаю расширение файла из полного пути к нему
        _, extension = os.path.splitext(file_path)
        
        # Если нужно добавить точку перед расширением, добавляю её
        return extension if with_dot else extension.lstrip('.')
    
    @staticmethod
    def extract_file_name_without_extension (file_path: str) -> str:
        # Имя файла без пути к нему
        file_name_only = File.extract_file_name(file_path)
        
        # Расширение файла
        file_extension = File.extract_file_extension(file_path)
        
        # Возвращаем имя файла без пути к нему и расширения
        return file_name_only[:-len(file_extension)]
    
    @staticmethod
    def relative_path (full_path: str, base_path: str) -> str | bool:
        """
        Возвращает относительный путь к файлу относительно заданной директории.
        :param full_path: Полный путь к файлу.
        :param base_path: Базовая директория.
        :return: str|bool: Относительный путь к файлу или False, если путь не относится к заданной директории.
        """
        return full_path[len(base_path):] if base_path.lower() in full_path.lower() else False
    
    @staticmethod
    def size (file_name: str, error_localization: dict[str, str] | None = None) -> ActionState[int]:
        """
        Получает размер файла и формирует результат с возможными ошибками.

        :param file_name: Путь к файлу.
        :param error_localization: Локализации сообщений об ошибках. Ече если None, используются сообщения по умолчанию. По умолчанию: None
        :return: Объект ActionState с размером файла или ошибками.
        """
        # Создаем результат
        result = ActionState(-1)
        
        # Если не заданы сообщения об ошибках
        if error_localization is None:
            # - устанавливаем сообщения по умолчанию
            error_localization = File.FILE_SIZE_ERROR_MESSAGES
        
        # Проверяем существование файла
        if not os.path.exists(file_name):
            # - если файл не существует, добавляем ошибку
            result.add_error(error_localization['file_not_exist'])
            # - возвращаем результат
            return result
        
        # Проверяем, что это именно файл
        if not os.path.isfile(file_name):
            # - если это не файл, добавляем ошибку
            result.add_error(error_localization['not_a_file'])
            # - возвращаем результат
            return result
        
        # Пробуем получить размер файла
        try:
            size = os.path.getsize(file_name)
            # - если размер файла получен успешно, добавляем его в результат
            result.value = size
        except OSError:
            # - если возникла ошибка при получении размера файла, добавляем ошибку
            result.add_error(error_localization['cannot_get_size'])
        
        # Возвращаем результат
        return result
    
    @staticmethod
    def size_to_string (
            file_size: int, localize_file_size: dict[str, str] | None = None, decimal_separator: str = '.'
            ) -> str:
        """
        Преобразует размер файла в строку с локализацией.
        :param file_size: Размер файла в байтах.
        :param localize_file_size: Словарь локализации размеров файлов. Если None, используются значения по умолчанию. По умолчанию: None.
        :param decimal_separator: Разделитель дробной части числа. По умолчанию: '.'.
        :return: str: Строка с размером файла.
        """
        # Если не заданы локализации размеров файлов
        if localize_file_size is None:
            # - устанавливаем локализации по умолчанию
            localize_file_size = File.FILE_SIZE_UNITS
        
        # Вычисление степени для преобразования: берём минимум из 4 и результата округления до ближайшего целого числа
        # в меньшую сторону логарифма размера файла в байтах по основанию 1024 (это показывает, сколько раз нужно
        # разделить размер файла на 1024, чтобы получить значение в более крупных единицах измерения). Ограничение в 4
        # необходимо для того, чтобы соответствовать единице измерения ТБ (терабайт).
        power = min(4, math.floor(math.log(file_size, 1024))) if file_size > 0 else 0
        
        # Преобразование размера файла: размер файла делим на 1024 в степени, равной степени $power,
        # затем округляем полученное до 2 цифр после запятой.
        size = round(file_size / (1024 ** power), 2)
        
        # Возвращаем преобразованное значение вместе с единицей измерения
        return f"{size:,.2f} {localize_file_size[power]}".replace('.', decimal_separator)
    
    @staticmethod
    def hash (file_name: str, hash_algorithm: str = 'sha256') -> str:
        """
        Вычисляет хэш файла.
        :param file_name: Имя файла для которого нужно вычислить хэш.
        :param hash_algorithm: Алгоритм хэширования. По умолчанию: 'sha256'.
        :return: Строка с хэшем.
        """
        # Преобразование алгоритма в нижний регистр
        hash_algorithm = hash_algorithm.lower()
        
        # Определяем алгоритм хэширования
        match hash_algorithm:
            # md5
            case 'md5':
                hasher = hashlib.md5()
            # sha1
            case 'sha1':
                hasher = hashlib.sha1()
            # sha256
            case 'sha256':
                hasher = hashlib.sha256()
            # sha512
            case 'sha512':
                hasher = hashlib.sha512()
            # sha3_256
            case 'sha3_256':
                hasher = hashlib.sha3_256()
            # sha3_512
            case 'sha3_512':
                hasher = hashlib.sha3_512()
            # blake2b
            case 'blake2':
                hasher = hashlib.blake2b()
            # по умолчанию
            case _:
                hasher = hashlib.sha256()
        
        # Открываем файл для чтения
        with open(file_name, 'rb') as file:
            # - читаем файл по 4096 байт, чтобы сэкономить память
            while chunk := file.read(4096):
                # - добавляем прочитанные данные в хэш
                hasher.update(chunk)
        
        # Возвращаем hex-представление хэша
        return hasher.hexdigest()