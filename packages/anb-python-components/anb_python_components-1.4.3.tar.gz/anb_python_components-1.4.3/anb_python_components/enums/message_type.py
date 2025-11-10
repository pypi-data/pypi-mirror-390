# anb_python_components/enums/message_type.py

from enum import Enum

class MessageType(Enum):
    """
    Перечисление типов сообщений:
    - SUCCESS: Успешное выполнение.
    - INFO: Информация.
    - WARNING: Предупреждение.
    - ERROR: Ошибка.
    """
    # Успешное выполнение
    SUCCESS = 0
    
    # Информация
    INFO = 1
    
    # Предупреждение
    WARNING = 2
    
    # Ошибка
    ERROR = 3
    
    def __str__ (self):
        """
        Переопределение метода __str__.
        :return: Текстовое представление перечисления.
        """
        # Получаем текстовое представление
        match self:
            case MessageType.SUCCESS:
                result = "Успех"
            case MessageType.INFO:
                result = "Информация"
            case MessageType.WARNING:
                result = "Предупреждение"
            case MessageType.ERROR:
                result = "Ошибка"
            case _:
                result = "Неизвестный тип сообщения"
        
        # Возвращаем результат
        return result