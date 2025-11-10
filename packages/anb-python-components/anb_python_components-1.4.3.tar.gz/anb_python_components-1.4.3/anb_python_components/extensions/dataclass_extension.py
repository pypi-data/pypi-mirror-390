# anb_python_components/extensions/dataclass_extension.py
import copy
from dataclasses import Field, field
from typing import Any

from anb_python_components.extensions.type_extension import TypeExtension

class DataClassExtension:
    """
    Класс для расширения функциональности класса Field.
    """
    
    @staticmethod
    def define (default: Any = None, metadata: dict[str, Any] = None) -> Field:
        """
        Определяет поле с расширенными метаданными.
        :param default: Значение по умолчанию для поля.
        :param metadata: Метаданные для поля.
        :return: Объект поля.
        """
        # Создаём словарь метаданных
        meta = {} if metadata is None else metadata
        
        # Если значение по умолчанию не передано
        if default is None:
            # - то создаём поле без значения по умолчанию
            return field(metadata = meta)
        
        # Если значение по умолчанию передано неизменяемым типом, то создаём поле с этим значением по умолчанию, иначе с функцией-фабрикой
        return field(default = default, metadata = meta) if TypeExtension.check_immutability(default) else field(
                default_factory = lambda: copy.copy(default), metadata = meta
                )
    
    @staticmethod
    def defines (default: Any, *fields: Field) -> Field:
        """
        Определяет поле с расширенными метаданными и переданными полями.
        :param default: Значение по умолчанию для поля.
        :param fields: Поля для расширения.
        :return: Объект поля.
        """
        # Создаём словарь метаданных
        metas = {}
        
        # Проверяем, что все аргументы — экземпляры Field
        for i, f in enumerate(fields):
            # - если хоть один аргумент не является полем
            if not isinstance(f, Field):
                # -- то создаём текстовое описание ошибки
                error = [
                        f"Аргумент fields[{i}] должен быть экземпляром dataclasses.Field, получено {type(f).__name__}",
                        f"Argument fields[{i}] must be an instance of dataclasses.Field, got {type(f).__name__}"
                        ]
                # -- и выбрасываем исключение
                raise TypeError("\n".join(error))
        
        # Собираем все метаданные из переданных полей
        for f in fields:
            if f.metadata:
                metas.update(f.metadata)
        
        return DataClassExtension.define(default, metas)