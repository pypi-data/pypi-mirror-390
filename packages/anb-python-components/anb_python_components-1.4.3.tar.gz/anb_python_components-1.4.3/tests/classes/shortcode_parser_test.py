# shortcode_parser_test.py

import unittest

from anb_python_components.classes.shortcode_parser import ShortCodeParser

class ShortCodeParserTest(unittest.TestCase):
    @staticmethod
    def create_parser () -> ShortCodeParser:
        parser = ShortCodeParser()
        
        parser.add_short_code(
                'test', lambda content, params: f"Это тестовый текст - {content}",
                lambda content, params: f"Это тело - {content}",
                lambda content, params: not content is None
                )
        
        parser.add_short_code(
                'test2', lambda content, params: f"Это вложенный тестовый текст - {content}",
                lambda content, params: f"Это тело - {content}",
                lambda content, params: not content is None
                )
        
        parser.add_short_code(
                'test3', lambda content, params: f"Это вложенный тестовый текст - {content}",
                lambda content, params: f"Это тело - {content}",
                lambda content, params: not content is None
                )
        
        parser.add_short_code(
                'test4', lambda content, params: f"Это вложенный тестовый текст - {content}",
                lambda content, params: f"Это тело - {content}",
                lambda content, params: not content is None
                )
        
        return parser
    
    def test_parse (self):
        parser = ShortCodeParserTest.create_parser()
        
        # Тест 1: без вложенности тегов
        
        text1 = """
            [test ignore="test" param="value"]Это текст[/test]
        """
        
        parsed1 = parser.parse(text1)
        
        expected1 = """
            Это тестовый текст - Это текст
        """
        
        self.assertEqual(expected1, parsed1)
        
        # Тест 2: с вложенностью тегов и отсутствием ограничений на вложенность
        
        text2 = """
            [test ignore="test" param="value"]Инспектируем вложенность [test2]Это текст 2 уровня[test3]Это текст 3 уровня[test4]Это текст 4 уровня[/test4][/test3][/test2][/test]
        """
        
        parsed2 = parser.parse(text2)
        
        expected2 = """
            Это тестовый текст - Инспектируем вложенность Это вложенный тестовый текст - Это текст 2 уровняЭто вложенный тестовый текст - Это текст 3 уровняЭто вложенный тестовый текст - Это текст 4 уровня
        """
        
        self.assertEqual(expected2, parsed2)
        
        # Тест 3: с вложенностью тегов и ограничениями на вложенность
        
        parsed3 = parser.parse(text2, True)
        expected3 = """
            Это тестовый текст - Инспектируем вложенность [test2]Это текст 2 уровня[test3]Это текст 3 уровня[test4]Это текст 4 уровня[/test4][/test3][/test2]
        """
        
        self.assertEqual(expected3, parsed3)
        
        # Тест 4: с отключением обработки тегов
        
        parsed4 = parser.parse(text1, is_unset = True)
        
        expected4 = """
            Это тело - Это текст
        """
        
        self.assertEqual(expected4, parsed4)
        
        parsed5 = parser.parse(text2, is_unset = True)
        
        expected5 = """
            Это тело - Инспектируем вложенность Это тело - Это текст 2 уровняЭто тело - Это текст 3 уровняЭто тело - Это текст 4 уровня
        """
        
        self.assertEqual(expected5, parsed5)
        
        parsed6 = parser.parse(text2, True, True)
        
        expected6 = """
            Это тело - Инспектируем вложенность [test2]Это текст 2 уровня[test3]Это текст 3 уровня[test4]Это текст 4 уровня[/test4][/test3][/test2]
        """
        
        self.assertEqual(expected6, parsed6)

if __name__ == '__main__':
    unittest.main()