# rk/__init__.py
"""
RK.rubyKit - Python library for developing apps for RubyOS
Release: December 2025 - January 2026
"""

__version__ = "0.1.0"
__author__ = "RubyKit Team"

import os
import subprocess
from typing import Optional, Dict, Any


class UI:
    """UI namespace for interface components"""
    pass


class Mask:
    """Mask class for UI masking operations"""
    def __init__(self, ui_type):
        self.ui_type = ui_type
        self.elements = []
    
    def add_element(self, element):
        self.elements.append(element)


class Box:
    """Box UI element with coordinate positioning"""
    def __init__(self, x: float = 0, y: float = 0, z: int = 1):
        self.x = x
        self.y = y
        self.z = z
        self.coordinates = {"x": x, "y": y, "z": z}
    
    @classmethod
    def new(cls, x: float = 0, y: float = 0, z: int = 1):
        """Create a new box at specified coordinates"""
        return cls(x, y, z)


class Machine:
    """Machine operations for reading external code"""
    @staticmethod
    def Know(mask: Mask, line_number: int):
        """
        Read and understand code from external files
        Args:
            mask: The mask context
            line_number: Line number to read from
        """
        return {"mask": mask, "line": line_number}


class String:
    """String creation and editing"""
    def __init__(self, font: str, text_type: str, content: str):
        self.font = font
        self.text_type = text_type
        self.content = content
    
    @classmethod
    def create(cls, font: str = "Arial", text_type: str = "Text", content: str = ""):
        """Create a text string with specified font"""
        return cls(font, text_type, content)


class RubyKit:
    """Main RubyKit compiler and runtime"""
    
    def __init__(self):
        self.commands = {}
        self.xa_blocks = {}
    
    @staticmethod
    def compile_sh(def_file: str, app_name: str) -> bool:
        """
        Compile a Ruby app
        Args:
            def_file: Path to def.py file
            app_name: Name of the app to compile
        Returns:
            bool: Success status
        """
        try:
            # Check if def.py exists
            if not os.path.exists(def_file):
                raise FileNotFoundError(f"Definition file {def_file} not found")
            
            # Check if app.rk exists
            rk_file = f"{app_name}.rk"
            if not os.path.exists(rk_file):
                raise FileNotFoundError(f"RubyKit file {rk_file} not found")
            
            # Compilation logic
            print(f"Compiling {app_name}...")
            print(f"Loading definitions from {def_file}")
            print(f"Processing RubyKit file {rk_file}")
            
            # Read and process the .rk file
            with open(rk_file, 'r') as f:
                rk_content = f.read()
            
            # Create output directory if it doesn't exist
            output_dir = f"compiled/{app_name}"
            os.makedirs(output_dir, exist_ok=True)
            
            # Write compiled output
            output_file = f"{output_dir}/{app_name}_compiled.rk"
            with open(output_file, 'w') as f:
                f.write(f"# Compiled RubyKit Application: {app_name}\n")
                f.write(f"# Original: {rk_file}\n")
                f.write(f"# Definitions: {def_file}\n\n")
                f.write(rk_content)
            
            print(f"Compilation successful! Output: {output_file}")
            return True
            
        except Exception as e:
            print(f"Compilation failed: {str(e)}")
            return False
    
    def host(self, cmd: int, command: Any):
        """Host a command on a specific port"""
        self.commands[cmd] = command
    
    def run(self, xa_range: str):
        """Run xa blocks in specified range (e.g., 'x1-x3')"""
        print(f"Running {xa_range}...")
        # Parse range and execute


# Helper functions
def mask(ui_type) -> Mask:
    """Create a new mask"""
    return Mask(ui_type)


def coordinates(x: float = 0, y: float = 0, z: int = 1) -> Dict[str, float]:
    """Create coordinate dictionary"""
    return {"x": x, "y": y, "z": z}


def line(line_num: str, header: str, **kwargs) -> Dict[str, Any]:
    """Reference a line from def.py with header type"""
    return {"line": line_num, "header": header, **kwargs}


def string(font_text: str, content: str) -> String:
    """
    Create a text string
    Args:
        font_text: Format as 'Font:Type' (e.g., 'Arial:Text')
        content: The text content
    """
    parts = font_text.split(':')
    font = parts[0] if len(parts) > 0 else "Arial"
    text_type = parts[1] if len(parts) > 1 else "Text"
    return String.create(font, text_type, content)


def make_header(size: int):
    """Create RK header with specified size"""
    return f"RK_HEADER_{size}"


def host(cmd: int):
    """Host command on specified port"""
    return f"HOST_CMD_{cmd}"


def compile(app_name: str):
    """
    Compile a RubyKit application
    Args:
        app_name: Name of the application to compile
    """
    rk = RubyKit()
    success = rk.compile_sh("def.py", app_name)
    if success:
        print("Finished installing.")
    else:
        print("Compilation failed.")


# Export main classes and functions
__all__ = [
    'RubyKit',
    'UI',
    'Mask',
    'Box',
    'Machine',
    'String',
    'mask',
    'coordinates',
    'line',
    'string',
    'make_header',
    'host',
    'compile'
]
