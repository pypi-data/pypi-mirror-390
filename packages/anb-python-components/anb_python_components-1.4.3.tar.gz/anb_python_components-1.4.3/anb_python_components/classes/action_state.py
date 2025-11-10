# anb_python_components/classes/action_state.py
import copy
from typing import Callable

from anb_python_components.enums.message_type import MessageType
from anb_python_components.exceptions.wrong_type_exception import WrongTypeException
from anb_python_components.models.action_state_message import ActionStateMessage

# noinspection Annotator
class ActionState[T]:
    """
    Класс для хранения состояния действия.
    """
    
    def __init__ (self, default: T | None = None):
        self.__messages: list[ActionStateMessage] = []
        self.value: T | None = copy.deepcopy(default) if default is not None else None
    
    @staticmethod
    def get_string_error_only () -> Callable[[ActionStateMessage], bool]:
        """
        Возвращает лямбду для фильтрации только сообщений типа ERROR.
        """
        return lambda message: message.message_type == MessageType.ERROR
    
    @staticmethod
    def get_string_error_and_warning () -> Callable[[ActionStateMessage], bool]:
        """
        Возвращает лямбду для фильтрации сообщений типа ERROR и WARNING.
        """
        return lambda message: message.message_type in [MessageType.ERROR, MessageType.WARNING]
    
    @staticmethod
    def get_string_all () -> Callable[[ActionStateMessage], bool]:
        """
        Возвращает лямбду для фильтрации всех сообщений.
        """
        return lambda message: True
    
    def add_message (self, message: ActionStateMessage):
        """
        Добавляет сообщение в список.
        :param message: Сообщение.
        """
        if message:
            self.__messages.append(message)
        else:
            raise ValueError("Сообщение не может быть пустым.")
    
    def add (self, message_type: MessageType, message: str, flags: dict[str, bool] | None = None):
        """
        Добавляет сообщение в список.
        :param message_type: Тип сообщения.
        :param message: Сообщение.
        :param flags: Флаги (необязательный).
        """
        # Создаём сообщение
        message = ActionStateMessage(message_type, message, flags)
        
        # Добавляем в список
        self.add_message(message)
    
    def add_info (self, message: str, flags: dict[str, bool] | None = None):
        """
        Добавляет информационное сообщение в список.
        :param message: Сообщение.
        :param flags: Флаги (необязательный).
        """
        self.add(MessageType.INFO, message, flags)
    
    def add_warning (self, message: str, flags: dict[str, bool] | None = None):
        """
        Добавляет предупреждающее сообщение в список.
        :param message: Сообщение.
        :param flags: Флаги (необязательный).
        """
        self.add(MessageType.WARNING, message, flags)
    
    def add_error (self, message: str, flags: dict[str, bool] | None = None):
        """
        Добавляет сообщение об ошибке в список.
        :param message: Сообщение.
        :param flags: Флаги (необязательный).
        """
        self.add(MessageType.ERROR, message, flags)
    
    def add_state (self, state, clear_all_before: bool = False):
        """
        Добавляет другое состояние действия в текущее.
        :param state:ActionState - Состояние действия.
        :param clear_all_before - Очистить список перед добавлением (по умолчанию - False).
        
        ВНИМАНИЕ! Метод не передаёт значение value состояния, а просто переносит его сообщения.
        """
        # Проверяем тип
        if not isinstance(state, ActionState):
            # - и если не ActionState, то бросаем исключение
            raise WrongTypeException("Неверный тип состояния действия.", "ActionState", str(type(state)), "state")
        
        # Если нужно очистить список перед добавлением
        if clear_all_before:
            # - то очищаем его
            self.__messages.clear()
        
        # Получаем список сообщений из состояния
        state_messages = state.get_messages()
        
        # Перебираем все сообщения переданного состояния
        for state_message in state_messages:
            # - и если это сообщение состояния
            if isinstance(state_message, ActionStateMessage):
                # -- то добавляем его в текущий список
                self.__messages.append(state_message)
    
    def get_messages (self, predicate: Callable[[ActionStateMessage], bool] | None = None) -> list[ActionStateMessage]:
        """
        Возвращает список сообщений с учетом условия (если указан).
        :param predicate: Условие выборки.
        :return: Список сообщений.
        """
        # Если условие указано
        if predicate:
            # - то фильтруем список по нему
            return list(filter(predicate, self.__messages))
        else:
            # - если нет, то просто возвращаем весь список
            return self.__messages.copy()
    
    def get_string_messages (
            self, predicate: Callable[[ActionStateMessage], bool] | None = None, separator: str = "\n"
            ) -> str:
        """
        Возвращает строку сообщений с учетом условия (если указано).
        :param predicate: Условие выборки (необязательный).
        :param separator: Разделитель строк (необязательный, по умолчанию - "\n").
        :return: Строка сообщений.
        """
        # Получаем список сообщений с учетом условия
        messages = self.get_messages(predicate)
        
        # Объединяем их в строку и возвращаем
        return separator.join(map(lambda message: message.message, messages))
    
    def has_infos (self) -> bool:
        """
        Проверяет, есть ли в списке информационные сообщения.
        :return: True, если есть, иначе False.
        """
        return any(message.message_type == MessageType.INFO for message in self.__messages)
    
    def has_warnings (self) -> bool:
        """
        Проверяет, есть ли в списке предупреждающие сообщения.
        :return: True, если есть, иначе False.
        """
        return any(message.message_type == MessageType.WARNING for message in self.__messages)
    
    def has_errors (self) -> bool:
        """
        Проверяет, есть ли в списке сообщения об ошибках.
        :return: True, если есть, иначе False.
        """
        return any(message.message_type == MessageType.ERROR for message in self.__messages)
    
    def is_success (self, ignore_warnings: bool = False) -> bool:
        """
        Проверяет, успешное ли состояние действия.
        :param ignore_warnings: Игнорировать предупреждения (по умолчанию - False).
        :return: Успешно ли состояние действия.
        """
        # Задаем начальное значение результата
        result = True
        
        # Если не нужно игнорировать предупреждения
        if not ignore_warnings:
            # - то проверяем наличие предупреждений
            result = result and not self.has_warnings()
        
        # Проверяем наличие ошибок
        result = result and not self.has_errors()
        
        # Выдаём результат
        return result
    
    def clear (self, predicate: Callable[[ActionStateMessage], bool] | None = None):
        """
        Очищает список сообщений с учетом условия (если указан).
        :param predicate: Функция для фильтрации сообщений для очистки.
        """
        # Если условие указано
        if predicate:
            # - то фильтруем список
            self.__messages = list(filter(lambda message: not predicate(message), self.__messages))
        else:
            # - если нет, то просто очищаем список
            self.__messages.clear()
    
    def count (self, predicate: Callable[[ActionStateMessage], bool] | None = None) -> int:
        """
        Возвращает количество сообщений в списке с учетом условия (если указано).
        :param predicate: Условие выборки (необязательный).
        :return: Количество сообщений.
        """
        # Если условие указано
        if predicate:
            # - то фильтруем список по нему
            messages = self.get_messages(predicate)
            
            # - и возвращаем его длину
            return len(messages)
        else:
            # - если нет, то просто возвращаем длину списка
            return len(self.__messages)