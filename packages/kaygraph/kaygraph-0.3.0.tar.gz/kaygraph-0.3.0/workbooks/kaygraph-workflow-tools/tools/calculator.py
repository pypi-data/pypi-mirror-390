"""
Calculator tool implementation.
"""

import ast
import operator
import math
from typing import Dict, Any, Union


class SafeCalculator:
    """Safe mathematical expression evaluator."""
    
    # Allowed operators
    operators = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.Pow: operator.pow,
        ast.Mod: operator.mod,
        ast.USub: operator.neg,
        ast.UAdd: operator.pos,
    }
    
    # Allowed functions
    functions = {
        'abs': abs,
        'round': round,
        'min': min,
        'max': max,
        'sum': sum,
        'sqrt': math.sqrt,
        'log': math.log,
        'log10': math.log10,
        'sin': math.sin,
        'cos': math.cos,
        'tan': math.tan,
        'pi': math.pi,
        'e': math.e,
    }
    
    def evaluate(self, expression: str) -> Union[float, int]:
        """Safely evaluate a mathematical expression."""
        try:
            # Parse the expression
            node = ast.parse(expression, mode='eval')
            return self._eval_node(node.body)
        except Exception as e:
            raise ValueError(f"Invalid expression: {e}")
    
    def _eval_node(self, node):
        """Recursively evaluate AST nodes."""
        if isinstance(node, ast.Constant):
            return node.value
        elif isinstance(node, ast.Num):  # For older Python versions
            return node.n
        elif isinstance(node, ast.BinOp):
            left = self._eval_node(node.left)
            right = self._eval_node(node.right)
            return self.operators[type(node.op)](left, right)
        elif isinstance(node, ast.UnaryOp):
            operand = self._eval_node(node.operand)
            return self.operators[type(node.op)](operand)
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                func_name = node.func.id
                if func_name in self.functions:
                    args = [self._eval_node(arg) for arg in node.args]
                    return self.functions[func_name](*args)
            raise ValueError(f"Function not allowed: {ast.dump(node.func)}")
        elif isinstance(node, ast.Name):
            if node.id in self.functions:
                return self.functions[node.id]
            raise ValueError(f"Name not allowed: {node.id}")
        else:
            raise ValueError(f"Unsupported operation: {type(node)}")


def calculate(expression: str) -> Dict[str, Any]:
    """
    Safely evaluate a mathematical expression.
    
    Supports:
    - Basic operations: +, -, *, /, **, %
    - Functions: abs, round, min, max, sum, sqrt, log, log10, sin, cos, tan
    - Constants: pi, e
    """
    calculator = SafeCalculator()
    
    try:
        result = calculator.evaluate(expression)
        
        # Format result nicely
        if isinstance(result, float):
            # Round to reasonable precision
            if result == int(result):
                result = int(result)
            else:
                result = round(result, 10)
        
        return {
            "success": True,
            "expression": expression,
            "result": result,
            "type": type(result).__name__
        }
    except Exception as e:
        return {
            "success": False,
            "expression": expression,
            "error": str(e)
        }


def solve_equation(equation: str) -> Dict[str, Any]:
    """
    Solve simple equations (limited functionality).
    For now, just evaluates expressions.
    """
    # Remove spaces and handle basic equation format
    equation = equation.replace(" ", "")
    
    # If it's an equation (has =), try to evaluate both sides
    if "=" in equation:
        parts = equation.split("=")
        if len(parts) == 2:
            left_result = calculate(parts[0])
            right_result = calculate(parts[1])
            
            if left_result["success"] and right_result["success"]:
                return {
                    "success": True,
                    "equation": equation,
                    "left_side": left_result["result"],
                    "right_side": right_result["result"],
                    "equal": left_result["result"] == right_result["result"]
                }
    
    # Otherwise just calculate as expression
    return calculate(equation)


# Tool metadata for registration
TOOL_METADATA = {
    "name": "calculator",
    "description": "Perform mathematical calculations and evaluate expressions",
    "parameters": {
        "type": "object",
        "properties": {
            "expression": {
                "type": "string",
                "description": "Mathematical expression to evaluate (e.g., '2 + 2', 'sqrt(16)', 'sin(pi/2)')"
            }
        },
        "required": ["expression"]
    },
    "examples": [
        {"expression": "2 + 2"},
        {"expression": "sqrt(16) * 3"},
        {"expression": "sin(pi/2) + cos(0)"},
        {"expression": "log10(1000)"}
    ]
}


if __name__ == "__main__":
    # Test the calculator
    print("Testing calculator tool...")
    
    test_expressions = [
        "2 + 2",
        "10 * 5 - 3",
        "2 ** 10",
        "sqrt(16)",
        "sin(pi/2)",
        "log10(1000)",
        "max(1, 2, 3, 4, 5)",
        "sum([1, 2, 3, 4, 5])",
        "invalid expression",
        "10 / 0"  # Division by zero
    ]
    
    for expr in test_expressions:
        result = calculate(expr)
        print(f"\n{expr} = {result}")