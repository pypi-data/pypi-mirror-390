# anb_python_components/exceptions/wrong_type_exception.py

class WrongTypeException(Exception):
    """
    Ошибка, возникающая при попытке присвоить значение другого типа данным полям.
    """
    
    def __init__ (self, message: str = None, type_name: str = None, real_type_name: str = None, var_name: str = None):
        """
        Инициализация экземпляра класса WrongTypeException.
        :param message: Сообщение об ошибке.
        :param type_name: Имя типа (по умолчанию None).
        :param real_type_name: Имя реального типа (по умолчанию None).
        :param var_name: Имя переменной (по умолчанию None).
        """
        super().__init__(message)
        self.message = message
        self.type_name = type_name,
        self.real_type_name = real_type_name,
        self.var_name = var_name