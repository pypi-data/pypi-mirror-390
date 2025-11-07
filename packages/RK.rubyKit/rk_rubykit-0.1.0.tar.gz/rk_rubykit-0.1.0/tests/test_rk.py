"""
Unit tests for RK.rubyKit
"""

import unittest
import rk


class TestRubyKit(unittest.TestCase):
    
    def test_mask_creation(self):
        """Test mask creation"""
        ui_mask = rk.mask(rk.UI)
        self.assertIsInstance(ui_mask, rk.Mask)
    
    def test_box_creation(self):
        """Test box creation with coordinates"""
        box = rk.Box.new(x=10, y=20, z=2)
        self.assertEqual(box.x, 10)
        self.assertEqual(box.y, 20)
        self.assertEqual(box.z, 2)
    
    def test_coordinates(self):
        """Test coordinate dictionary creation"""
        coords = rk.coordinates(x=5, y=10, z=3)
        self.assertEqual(coords["x"], 5)
        self.assertEqual(coords["y"], 10)
        self.assertEqual(coords["z"], 3)
    
    def test_string_creation(self):
        """Test string creation"""
        text = rk.string("Arial:Text", "Hello World")
        self.assertIsInstance(text, rk.String)
        self.assertEqual(text.font, "Arial")
        self.assertEqual(text.content, "Hello World")
    
    def test_machine_know(self):
        """Test Machine.Know method"""
        ui_mask = rk.mask(rk.UI)
        result = rk.Machine.Know(ui_mask, 100)
        self.assertIsInstance(result, dict)
        self.assertEqual(result["line"], 100)


if __name__ == "__main__":
    unittest.main()
