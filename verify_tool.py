from google.adk.tools import FunctionTool

def my_func(a: int):
    """My function."""
    return a

try:
    t = FunctionTool(my_func)
    print("FunctionTool(func) worked")
except Exception as e:
    print(f"FunctionTool(func) failed: {e}")

try:
    t = FunctionTool.from_function(my_func)
    print("FunctionTool.from_function(func) worked")
except Exception as e:
    print(f"FunctionTool.from_function(func) failed: {e}")
