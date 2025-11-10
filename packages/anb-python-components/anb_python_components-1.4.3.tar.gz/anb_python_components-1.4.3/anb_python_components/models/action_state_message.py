# anb_python_components/models/action_state_message.py
from dataclasses import dataclass, field

from anb_python_components.enums.message_type import MessageType

@dataclass
class ActionStateMessage:
    """
    Модель сообщения о состояния действия.
    """
    # Тип сообщения (по умолчанию, INFO).
    message_type: MessageType = field(default_factory = lambda: MessageType.INFO)
    
    # Текст сообщения (по умолчанию, пустая строка).
    message: str = field(default = "")
    
    # Флаги сообщения (по умолчанию, пустой словарь).
    flags: dict[str, bool] = field(default_factory = dict)
    
    def __str__ (self):
        """
        Переопределение метода __str__.
        :return: Текстовое представление модели.
        """
        return f"[{str(self.message_type).upper()}] {self.message}"