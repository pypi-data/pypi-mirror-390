# action_state_test.py

import unittest

from anb_python_components.classes.action_state import ActionState, ActionStateMessage, MessageType

class ActionStateTest(unittest.TestCase):
    def test_init (self):
        state = ActionState[bool](False)
        self.assertIsInstance(state, ActionState)
        self.assertFalse(state.value)
        state.value = True
        self.assertTrue(state.value)
    
    def test_add_message (self):
        message = ActionStateMessage(MessageType.INFO, "Test message")
        
        state = ActionState[bool](False)
        state.add_message(message)
        
        self.assertEqual(1, state.count())
    
    @staticmethod
    def get_test_state (no_warning: bool = False, no_error: bool = False, state_value: bool = False) -> ActionState[
        bool]:
        """
        Генерирует тестовое состояние.
        :param no_warning: Без предупреждений.
        :param no_error: Без ошибок.
        :param state_value: Значение состояния.
        :return: Тестовое состояние.
        """
        state = ActionState[bool](False)
        
        state.add_info("Тестовое сообщение1")
        if not no_error:
            state.add_error("Тестовое сообщение2")
        state.add_info("Тестовое сообщение3")
        state.add_info("Тестовое сообщение4")
        if not no_warning:
            state.add_warning("Тестовое сообщение5")
        state.add_info("Тестовое сообщение6")
        state.add_info("Тестовое сообщение7")
        state.add_info("Тестовое сообщение8")
        if not no_warning:
            state.add_warning("Тестовое сообщение9")
        if not no_error:
            state.add_error("Тестовое сообщение10")
        
        state.value = state_value
        
        return state
    
    def test_add_state (self):
        state1 = ActionStateTest.get_test_state(True, True, True)
        
        state2 = ActionStateTest.get_test_state(state_value = False)
        
        state1.add_state(state2)
        
        self.assertEqual(16, state1.count())
    
    def test_get_messages (self):
        state = ActionStateTest.get_test_state()
        
        state_messages = state.get_messages()
        
        self.assertEqual(10, len(state_messages))
        
        count_errors = 0
        
        for message in state_messages:
            if message.message_type == MessageType.ERROR:
                count_errors += 1
        
        self.assertEqual(2, count_errors)
    
    def test_get_string_messages (self):
        state = ActionStateTest.get_test_state()
        
        state_message_string = state.get_string_messages(ActionState.get_string_error_only())
        
        need_string = "Тестовое сообщение2\nТестовое сообщение10"
        
        self.assertEqual(state_message_string, need_string)
    
    def test_has_infos (self):
        state = ActionStateTest.get_test_state()
        
        self.assertTrue(state.has_infos())
    
    def test_has_warnings (self):
        state = ActionStateTest.get_test_state()
        
        self.assertTrue(state.has_warnings())
    
    def test_has_errors (self):
        state = ActionStateTest.get_test_state()
        
        self.assertTrue(state.has_errors())
    
    def test_is_success (self):
        state_fail = ActionStateTest.get_test_state()
        state_success = ActionStateTest.get_test_state(no_warning = True, no_error = True)
        state_success_no_warning = ActionStateTest.get_test_state(no_error = True)
        
        self.assertTrue(state_success.is_success())
        self.assertTrue(state_success_no_warning.is_success(True))
        self.assertFalse(state_fail.is_success())
    
    def test_clear (self):
        state = ActionStateTest.get_test_state()
        
        state.clear(lambda message: message.message_type == MessageType.WARNING)
        
        self.assertEqual(8, len(state.get_messages()))
        
        state.clear()
        
        self.assertEqual(0, len(state.get_messages()))
    
    def test_count (self):
        state = ActionStateTest.get_test_state()
        
        count_all = state.count()
        count_warnings = state.count(lambda message: message.message_type == MessageType.WARNING)
        count_errors = state.count(lambda message: message.message_type == MessageType.ERROR)
        count_errors_and_warnings = state.count(
                lambda message: message.message_type == MessageType.WARNING or message.message_type == MessageType.ERROR
                )
        
        self.assertEqual(10, count_all)
        self.assertEqual(2, count_errors)
        self.assertEqual(2, count_warnings)
        self.assertEqual(4, count_errors_and_warnings)

if __name__ == '__main__':
    unittest.main()