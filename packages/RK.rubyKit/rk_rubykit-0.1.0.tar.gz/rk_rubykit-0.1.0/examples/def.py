# def.py - Example Python definitions
import time

def wait(seconds):
    """Wait for specified seconds"""
    time.sleep(seconds)
    print(f"Waited {seconds} seconds")

def coolFunc():
    """Example function"""
    print("Cool function executed!")
    return "Success"

def repeat(times, func):
    """Repeat a function multiple times"""
    for i in range(times):
        func()
