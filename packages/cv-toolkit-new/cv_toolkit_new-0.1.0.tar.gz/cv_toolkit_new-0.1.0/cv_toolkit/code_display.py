"""
Code Display Utility
Displays the source code of functions for educational and examination purposes.
"""

import inspect


def display_code(func):
    """
    Display the source code of a function.
    
    Args:
        func: Function object to display
    """
    print("\n" + "="*80)
    print(f"SOURCE CODE FOR: {func.__name__}")
    print("="*80)
    try:
        source = inspect.getsource(func)
        print(source)
    except Exception as e:
        print(f"Could not retrieve source code: {e}")
    print("="*80 + "\n")


def display_module_code(module_name):
    """
    Display all the source code from a module file.
    
    Args:
        module_name: Name of the module to display
    """
    print("\n" + "="*80)
    print(f"FULL MODULE CODE: {module_name}")
    print("="*80)
    try:
        import importlib
        module = importlib.import_module(f"cv_toolkit.{module_name}")
        source = inspect.getsource(module)
        print(source)
    except Exception as e:
        print(f"Could not retrieve module code: {e}")
    print("="*80 + "\n")


def show_code_and_run(func, *args, **kwargs):
    """
    Display the source code of a function and then execute it.
    
    Args:
        func: Function to display and run
        *args: Arguments to pass to the function
        **kwargs: Keyword arguments to pass to the function
    
    Returns:
        Result of the function execution
    """
    display_code(func)
    print("\nEXECUTING THE ABOVE CODE...")
    print("-"*80)
    result = func(*args, **kwargs)
    print("-"*80)
    print("EXECUTION COMPLETE\n")
    return result
