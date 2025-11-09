"""
errify - Human-Readable Error Handler for Python
Transforms confusing Python errors into beginner-friendly explanations.
"""

import sys
import traceback
from typing import Dict, Callable, Optional, Type
import re


class ErrorExplainer:
    """Maps Python exceptions to human-readable explanations."""
    
    def __init__(self):
        self.explanations: Dict[Type[Exception], Callable] = {
            NameError: self._explain_name_error,
            TypeError: self._explain_type_error,
            ValueError: self._explain_value_error,
            IndexError: self._explain_index_error,
            KeyError: self._explain_key_error,
            AttributeError: self._explain_attribute_error,
            ZeroDivisionError: self._explain_zero_division,
            ImportError: self._explain_import_error,
            ModuleNotFoundError: self._explain_module_not_found,
            SyntaxError: self._explain_syntax_error,
            IndentationError: self._explain_indentation_error,
            FileNotFoundError: self._explain_file_not_found,
            KeyboardInterrupt: self._explain_keyboard_interrupt,
            RecursionError: self._explain_recursion_error,
        }
    
    def register(self, exc_type: Type[Exception], handler: Callable):
        """Register a custom explanation handler for an exception type."""
        self.explanations[exc_type] = handler
    
    def explain(self, exc_type: Type[Exception], exc_value: Exception, tb) -> str:
        """Generate a human-readable explanation for an exception."""
        handler = self.explanations.get(exc_type, self._explain_generic)
        
        # Build the friendly message
        lines = []
        lines.append("=" * 70)
        lines.append("Oops! Python ran into a problem")
        lines.append("=" * 70)
        lines.append("")
        
        explanation = handler(exc_value, tb)
        lines.append(explanation)
        
        lines.append("")
        lines.append("-" * 70)
        lines.append("Where it happened:")
        lines.append("-" * 70)
        lines.append(self._format_traceback(tb))
        
        lines.append("")
        lines.append("Tip: Read the explanation above, check the line number,")
        lines.append("and review your code at that location.")
        lines.append("=" * 70)
        
        return "\n".join(lines)
    
    def _format_traceback(self, tb) -> str:
        """Format traceback in a readable way."""
        lines = []
        tb_lines = traceback.format_tb(tb)
        
        for line in tb_lines:
            # Extract file, line number, and code
            match = re.search(r'File "(.+)", line (\d+)', line)
            if match:
                file_path = match.group(1)
                line_num = match.group(2)
                
                # Get the code snippet
                code_match = re.search(r'\n    (.+)$', line)
                code = code_match.group(1) if code_match else ""
                
                lines.append(f"File: {file_path}")
                lines.append(f"Line: {line_num}")
                if code:
                    lines.append(f"Code: {code}")
                lines.append("")
        
        return "\n".join(lines) if lines else "  (No traceback available)"
    
    # Exception-specific explainers
    
    def _explain_name_error(self, exc: NameError, tb) -> str:
        msg = str(exc)
        var_match = re.search(r"'(\w+)'", msg)
        var_name = var_match.group(1) if var_match else "something"
        
        return f"""**NameError**: Python doesn't know what '{var_name}' is.

What happened:
   You tried to use a variable or function called '{var_name}',
   but Python hasn't seen it defined anywhere yet.

How to fix it:
   1. Check for typos: Did you spell '{var_name}' correctly?
   2. Make sure you defined '{var_name}' before using it
   3. If it's a variable, did you assign a value to it first?
   4. If it's from a library, did you import it?

Example:
   # Wrong:
   print(messge)  # typo!
   
   # Right:
   message = "Hello"
   print(message)"""
    
    def _explain_type_error(self, exc: TypeError, tb) -> str:
        msg = str(exc)
        
        return f"""**TypeError**: You're mixing incompatible types.

What happened:
   {msg}
   
   Python expected one type of data but got another.

How to fix it:
   1. Check what types of values you're working with
   2. Convert types if needed (e.g., str() or int())
   3. Make sure function arguments match what's expected

Example:
   # Wrong:
   result = "5" + 3  # can't add string and number
   
   # Right:
   result = 5 + 3  # both numbers
   # OR
   result = "5" + "3"  # both strings"""
    
    def _explain_value_error(self, exc: ValueError, tb) -> str:
        msg = str(exc)
        
        return f"""**ValueError**: The value you provided isn't valid.

What happened:
   {msg}
   
   Python got the right type, but the value itself doesn't work.
How to fix it:
   1. Check if you're converting data correctly
   2. Verify input values are in the expected format
   3. Handle invalid inputs with try/except

Example:
   # Wrong:
   number = int("hello")  # can't convert word to number
   
   # Right:
   number = int("42")  # valid number string"""
    
    def _explain_index_error(self, exc: IndexError, tb) -> str:
        return f"""**IndexError**: You tried to access an item that doesn't exist.

What happened:
   You tried to access a position in a list (or string) that's
   out of range. Remember: Python starts counting from 0!

How to fix it:
   1. Check the length of your list with len()
   2. Remember the last valid index is len(list) - 1
   3. Make sure your loop doesn't go too far

Example:
   # Wrong:
   my_list = [1, 2, 3]
   print(my_list[3])  # No 4th item! (0, 1, 2 are valid)
   
   # Right:
   print(my_list[2])  # Gets the 3rd item
   print(my_list[-1])  # Gets the last item"""
    
    def _explain_key_error(self, exc: KeyError, tb) -> str:
        key = str(exc).strip("'\"")
        
        return f"""**KeyError**: The dictionary key '{key}' doesn't exist.

What happened:
   You tried to access a key in a dictionary that isn't there.

How to fix it:
   1. Check if the key exists first using 'in'
   2. Use .get() method which returns None if key missing
   3. Verify you spelled the key correctly

Example:
   # Wrong:
   data = {{"name": "Alice"}}
   print(data["age"])  # 'age' key doesn't exist
   
   # Right:
   if "age" in data:
       print(data["age"])
   # OR
   print(data.get("age", "Not specified"))"""
    
    def _explain_attribute_error(self, exc: AttributeError, tb) -> str:
        msg = str(exc)
        
        return f"""**AttributeError**: That object doesn't have that attribute.

What happened:
   {msg}
   
   You tried to access a method or property that doesn't exist
   on this type of object.

How to fix it:
   1. Check the documentation for the correct method name
   2. Verify the object type is what you expect
   3. Look for typos in the method/attribute name

Example:
   # Wrong:
   my_list = [1, 2, 3]
   my_list.add(4)  # Lists use .append(), not .add()
   
   # Right:
   my_list.append(4)"""
    
    def _explain_zero_division(self, exc: ZeroDivisionError, tb) -> str:
        return f"""**ZeroDivisionError**: You can't divide by zero!

What happened:
   Your code tried to divide a number by zero, which is
   mathematically undefined (and breaks Python!).

How to fix it:
   1. Check if the divisor might be zero before dividing
   2. Add an if statement to handle the zero case
   3. Review your calculation logic

Example:
   # Wrong:
   result = 10 / 0
   
   # Right:
   divisor = 0
   if divisor != 0:
       result = 10 / divisor
   else:
       print("Can't divide by zero!")"""
    
    def _explain_import_error(self, exc: ImportError, tb) -> str:
        msg = str(exc)
        
        return f"""**ImportError**: Python couldn't import that module.

What happened:
   {msg}
   
   The module exists but something went wrong when loading it.

How to fix it:
   1. Check if the module is installed correctly
   2. Verify your import statement syntax
   3. Look for circular import issues

Example:
   # Make sure the package is installed:
   # pip install package_name"""
    
    def _explain_module_not_found(self, exc: ModuleNotFoundError, tb) -> str:
        msg = str(exc)
        module_match = re.search(r"'(\w+)'", msg)
        module_name = module_match.group(1) if module_match else "the module"
        
        return f"""**ModuleNotFoundError**: Python can't find '{module_name}'.

What happened:
   You tried to import '{module_name}', but it's not installed
   or Python doesn't know where to find it.

How to fix it:
   1. Install the package: pip install {module_name}
   2. Check for typos in the module name
   3. Make sure you're in the right Python environment

Example command:
   pip install {module_name}"""
    
    def _explain_syntax_error(self, exc: SyntaxError, tb) -> str:
        return f"""**SyntaxError**: Python doesn't understand your code.

What happened:
   {str(exc)}
   
   There's a typo or mistake in how you wrote your code.

How to fix it:
   1. Check for missing colons (:) after if, for, def, etc.
   2. Make sure all brackets/parentheses are closed
   3. Look for missing quotes around strings
   4. Check for misplaced commas or operators

Common mistakes:
   - Missing colon: if x > 5  (should be: if x > 5:)
   - Unclosed string: print("hello)
   - Unmatched brackets: my_list = [1, 2, 3"""
    
    def _explain_indentation_error(self, exc: IndentationError, tb) -> str:
        return f"""**IndentationError**: Your code isn't indented correctly.

What happened:
   Python is very picky about indentation (spaces/tabs).
   The code structure doesn't match Python's rules.

How to fix it:
   1. Use 4 spaces per indentation level (standard)
   2. Don't mix tabs and spaces
   3. Make sure code inside functions/loops is indented
   4. Check that related lines have the same indentation

Example:
   # Wrong:
   def greet():
   print("Hello")  # Not indented!
   
   # Right:
   def greet():
       print("Hello")  # Indented with 4 spaces"""
    
    def _explain_file_not_found(self, exc: FileNotFoundError, tb) -> str:
        msg = str(exc)
        
        return f"""**FileNotFoundError**: Python can't find that file.

What happened:
   {msg}
   
   You tried to open a file that doesn't exist or is in a
   different location.

How to fix it:
   1. Check the file name for typos
   2. Verify the file path is correct
   3. Use absolute paths or check your current directory
   4. Make sure the file actually exists!

Example:
   # Check if file exists first:
   import os
   if os.path.exists("myfile.txt"):
       with open("myfile.txt") as f:
           content = f.read()"""
    
    def _explain_keyboard_interrupt(self, exc: KeyboardInterrupt, tb) -> str:
        return f"""**KeyboardInterrupt**: You stopped the program.

What happened:
   You pressed Ctrl+C (or Cmd+C) to stop the program.
   This is normal and not an error!

This is usually intentional, but if it wasn't:
   - Maybe your program got stuck in an infinite loop
   - Or it was taking too long to complete"""
    
    def _explain_recursion_error(self, exc: RecursionError, tb) -> str:
        return f"""**RecursionError**: Your function calls itself too many times!

What happened:
   A function kept calling itself over and over until Python
   ran out of memory. This is called infinite recursion.

How to fix it:
   1. Add a base case to stop the recursion
   2. Make sure your recursive call gets closer to the base case
   3. Consider using a loop instead of recursion

Example:
   # Wrong - infinite recursion:
   def count_down(n):
       return count_down(n - 1)  # Never stops!
   
   # Right - has a base case:
   def count_down(n):
       if n <= 0:  # Base case
           return
       print(n)
       count_down(n - 1)"""
    
    def _explain_generic(self, exc: Exception, tb) -> str:
        exc_name = type(exc).__name__
        msg = str(exc)
        
        return f"""**{exc_name}**: Something went wrong.

What happened:
   {msg}

What to try:
   1. Read the error message carefully
   2. Check the line number where it happened
   3. Search online: "{exc_name} python"
   4. Look at the Python documentation for this error

This is a less common error type. The original message above
   might give you more specific clues."""


# Global explainer instance
_explainer = ErrorExplainer()


def excepthook(exc_type, exc_value, exc_tb):
    """Custom exception hook that shows friendly error messages."""
    if exc_type is KeyboardInterrupt:
        # Don't show full explanation for Ctrl+C
        print("\nProgram interrupted (Ctrl+C)")
        return
    
    explanation = _explainer.explain(exc_type, exc_value, exc_tb)
    print(explanation, file=sys.stderr)


def install():
    """Install errify as the default exception handler."""
    sys.excepthook = excepthook


def uninstall():
    """Restore the default Python exception handler."""
    sys.excepthook = sys.__excepthook__


def register_handler(exc_type: Type[Exception], handler: Callable):
    """Register a custom explanation handler for an exception type.
    
    Example:
        def my_handler(exc, tb):
            return "Custom explanation for this error"
        
        errify.register_handler(MyCustomError, my_handler)
    """
    _explainer.register(exc_type, handler)


# Auto-install on import (can be disabled by calling uninstall())
install()


# CLI Support
if __name__ == "__main__":
    import sys
    import runpy
    
    if len(sys.argv) < 2:
        print("Usage: python -m errify <script.py>")
        print("   or: python -m errify run <script.py>")
        sys.exit(1)
    
    # Handle 'run' command or direct script path
    script_path = sys.argv[2] if sys.argv[1] == "run" else sys.argv[1]
    
    # Remove errify args from sys.argv so the script sees correct args
    if sys.argv[1] == "run":
        sys.argv = [script_path] + sys.argv[3:]
    else:
        sys.argv = sys.argv[1:]
    
    # Install our hook
    install()
    
    # Run the script
    try:
        runpy.run_path(script_path, run_name="__main__")
    except Exception:
        # Exception will be caught by our custom hook
        pass