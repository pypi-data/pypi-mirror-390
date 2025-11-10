# tests/classes/interface_test.py
from __future__ import annotations

import unittest

from anb_python_components import Interface, implement, interface_required

class Drawable(Interface):
    @interface_required
    def draw (self) -> None: pass
    
    @interface_required
    def get_area (self) -> float: pass

class Renderable(Interface):
    @interface_required(lambda self, quality: int)
    def render (self, quality: int) -> bytes: pass

@implement(Drawable)
@implement(Renderable)
class Circle(Drawable, Renderable):
    def __init__ (self, radius: float):
        self.radius = radius
    
    def draw (self) -> None:
        print(f"Рисуем круг радиусом {self.radius}")
    
    def get_area (self) -> float:
        return 3.14159 * self.radius ** 2
    
    def render (self, quality: int) -> bytes:
        return b"PNG-data"

class InterfaceTest(unittest.TestCase):
    def test_interface (self):
        self.assertTrue(hasattr(Circle, '__implements_Drawable'))
    
    @staticmethod
    def check_drawable (drawable: Drawable):
        drawable.draw()
        return True
    
    def test_drawable (self):
        self.assertTrue(self.check_drawable(Circle(10)))

if __name__ == '__main__':
    unittest.main()