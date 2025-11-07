#!/usr/bin/env python3
"""
Example compilation script for RubyKit applications
"""

import rk

def main():
    print("Starting RubyKit compilation...")
    
    # Method 1: Using the shorthand compile function
    rk.compile("myApp")
    
    # Method 2: Using RubyKit class directly
    # rk_compiler = rk.RubyKit()
    # rk_compiler.compile_sh("def.py", "myApp")
    # print("Finished installing.")

if __name__ == "__main__":
    main()
