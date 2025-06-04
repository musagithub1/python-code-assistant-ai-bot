import unittest
from code_execution.code_executor import CodeExecutor

class TestCodeExecutor(unittest.TestCase):
    """Test cases for the CodeExecutor class."""
    
    def setUp(self):
        """Set up test environment."""
        self.code_executor = CodeExecutor(timeout=2)
    
    def test_execute_valid_code(self):
        """Test executing valid Python code."""
        code = "x = 5\ny = 10\nprint(x + y)"
        output, error, success = self.code_executor.execute_code(code)
        
        self.assertTrue(success)
        self.assertEqual(output.strip(), "15")
        self.assertEqual(error, "")
    
    def test_execute_code_with_syntax_error(self):
        """Test executing code with syntax error."""
        code = "print('Hello world'"  # Missing closing parenthesis
        output, error, success = self.code_executor.execute_code(code)
        
        self.assertFalse(success)
        self.assertEqual(output, "")
        self.assertTrue("Syntax Error" in error)
    
    def test_execute_code_with_runtime_error(self):
        """Test executing code with runtime error."""
        code = "print(undefined_variable)"
        output, error, success = self.code_executor.execute_code(code)
        
        self.assertFalse(success)
        self.assertEqual(output, "")
        self.assertTrue("Error" in error)
        self.assertTrue("undefined_variable" in error)
    
    def test_execute_code_with_output_and_error(self):
        """Test executing code that produces both output and error."""
        code = "print('Before error')\nprint(undefined_variable)\nprint('After error')"
        output, error, success = self.code_executor.execute_code(code)
        
        self.assertFalse(success)
        self.assertEqual(output.strip(), "Before error")
        self.assertTrue("Error" in error)
    
    def test_restricted_builtins(self):
        """Test that restricted builtins are properly blocked."""
        # Try to use open() which should be restricted
        code = "try:\n    f = open('test.txt', 'w')\n    print('Open succeeded')\nexcept Exception as e:\n    print(f'Open failed: {type(e).__name__}')"
        output, error, success = self.code_executor.execute_code(code)
        
        self.assertTrue(success)  # The code itself runs successfully
        self.assertTrue("Open failed" in output)  # But the open() function should fail
    
    def test_complex_calculation(self):
        """Test executing code with complex calculation."""
        code = """
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n-1)

result = factorial(5)
print(f"Factorial of 5 is {result}")
"""
        output, error, success = self.code_executor.execute_code(code)
        
        self.assertTrue(success)
        self.assertEqual(output.strip(), "Factorial of 5 is 120")
        self.assertEqual(error, "")

if __name__ == '__main__':
    unittest.main()
