# anb_python_components/classes/directory.py
import os
import platform
import subprocess

from anb_python_components.classes.action_state import ActionState

class Directory:
    """
    Класс для работы с директориями.
    """
    
    # Словарь сообщений об ошибках для удаления директории
    REMOVE_DIRECTORY_ERROR_MESSAGES: dict[str, str] = {
            'directory_not_exist': "Директория не существует или нет доступа на запись!",
            'error_deleting_directory': 'Ошибка удаления каталога: %s. Код возврата: %d!',
            'unhandled_error': 'Ошибка удаления директории %s: %s!'
            }
    
    @staticmethod
    def remove (directory: str, error_messages: dict[str, str] | None = None) -> ActionState[bool]:
        """
        Рекурсивно удаляет директорию с соответствующим результатом.

        :param directory: Путь к директории.
        :param error_messages: Слова для отображения ошибок. По умолчанию используются сообщения из REMOVE_DIRECTORY_ERROR_MESSAGES.
        :return: Объект ActionState с информацией о результате.
        """
        # Создаем объект ActionState для хранения результата
        result = ActionState[bool](False)
        
        # Если не заданы сообщения об ошибках
        if error_messages is None:
            # - устанавливаем сообщения по умолчанию
            error_messages = Directory.REMOVE_DIRECTORY_ERROR_MESSAGES
        
        try:
            # Проверяем существование директории
            if not Directory.is_exists(directory):
                # - если директория не существует, добавляем ошибку
                result.add_error(error_messages['directory_not_exist'])
                # - возвращаем результат
                return result
            
            # Определяем текущую операционную систему
            system_os = platform.system().lower()
            
            # Проверяем операционную систему. Если это Windows
            if system_os == 'windows':
                # - задаем команду для Windows
                command = ['cmd.exe', '/C', 'rd', '/S', '/Q', directory]
            else:
                # - иначе задаем команду для Unix-подобных систем
                command = ['rm', '-rf', directory]
            
            # Запуск команды с безопасностью (используется subprocess.run)
            process = subprocess.run(command, capture_output = True, text = True)
            
            # Анализируем код возврата процесса и если он не равен 0
            if process.returncode != 0:
                # - добавляем ошибку
                result.add_error(error_messages['error_deleting_directory'] % (directory, process.returncode))
                # - возвращаем результат
                return result
            
            # Установка успешного результата
            result.value = True
            
            # Возвращаем результат
            return result
        
        except Exception as ex:
            # Обработка необработанных исключений
            result.add_error(error_messages['unhandled_error'] % (directory, str(ex)))
            return result
    
    @staticmethod
    def is_exists (directory: str, check_access_level: str = '') -> bool:
        """
        Проверяет существование директории и доступность по правам доступа.

        :param directory: Путь к директории.
        :param check_access_level: Строка, содержащая символы 'r', 'w' и 'x', которые указывают на необходимость проверки прав доступа на чтение, запись и исполнение соответственно. Если строка пустая, проверка прав доступа не выполняется. Если нет какого-либо символа, проверка прав доступа не выполняется для этого типа прав. По умолчанию: ''.
        :return: True, если директория существует и доступна, иначе False.
        """
        # Проверяем существование директории
        if not os.path.exists(directory):
            # - и если директория не существует, возвращаем False
            return False
        
        # Проверяем, что это именно директория, а не файл
        if not os.path.isdir(directory):
            # - если это не директория, возвращаем False
            return False
        
        # Задаем флаги проверки прав доступа
        access_level_check = check_access_level.lower()
        
        # Проверяем права на чтение, если это требуется
        if 'r' in access_level_check and not os.access(directory, os.R_OK):
            # - если нет прав на чтение, возвращаем False
            return False
        
        # Проверяем права на запись, если это требуется
        if 'w' in access_level_check and not os.access(directory, os.W_OK):
            # - если нет прав на запись, возвращаем False
            return False
        
        # Проверяем права на исполнение, если это требуется
        if 'x' in access_level_check and not os.access(directory, os.X_OK):
            # - если нет прав на запись, возвращаем False
            return False
        
        # Если все проверки успешны, возвращаем True
        return True