import pytest

from universal_mcp.agents.sandbox import Sandbox


def test_simple_execution():
    sandbox = Sandbox()
    code = "print('hello world')"
    result = sandbox.run(code)
    assert result["stdout"].strip() == "hello world"
    assert result["success"]
    assert result["stderr"] == ""
    assert sandbox.context == {}


def test_variable_assignment():
    sandbox = Sandbox()
    code = "x = 10"
    result = sandbox.run(code)
    assert result["stdout"] == ""
    assert result["success"]
    assert sandbox.context == {"x": 10}


def test_use_previous_context():
    sandbox = Sandbox()
    sandbox.context = {"x": 5}
    code = "y = x * 2"
    result = sandbox.run(code)
    assert result["stdout"] == ""
    assert result["success"]
    assert sandbox.context == {"x": 5, "y": 10}


def test_execution_error():
    sandbox = Sandbox()
    code = "1 / 0"
    result = sandbox.run(code)
    assert "ZeroDivisionError: division by zero" in result["stderr"]
    assert not result["success"]
    assert sandbox.context == {}


def test_context_is_maintained_after_error():
    sandbox = Sandbox()
    # Run 1: define a variable
    result1 = sandbox.run("x = 10")
    assert result1["success"]
    assert sandbox.context == {"x": 10}

    # Run 2: introduce an error
    result2 = sandbox.run("y = z + 1")  # NameError: name 'z' is not defined
    assert not result2["success"]
    assert "NameError" in result2["stderr"]

    # Context should not be updated with 'y' but 'x' should still be there
    assert sandbox.context == {"x": 10}

    # Run 3: check if context is still valid
    result3 = sandbox.run("print(f'x is {x}')")
    assert result3["success"]
    assert result3["stdout"].strip() == "x is 10"


def test_fibonacci_generator_and_execution():
    sandbox = Sandbox()
    # Step 1: Define the Fibonacci generator function
    fib_def_code = """
def fibonacci(n):
    a, b = 0, 1
    for _ in range(n):
        yield a
        a, b = b, a + b
"""
    result1 = sandbox.run(fib_def_code)
    assert result1["success"]
    assert "fibonacci" in sandbox.context
    assert callable(sandbox.context["fibonacci"])

    # Step 2: Call the generator and print the results
    fib_call_code = """
fib_gen = fibonacci(8)
result_list = list(fib_gen)
print(result_list)
"""
    result2 = sandbox.run(fib_call_code)
    assert result2["success"]
    assert result2["stdout"].strip() == "[0, 1, 1, 2, 3, 5, 8, 13]"
    assert "result_list" in sandbox.context
    assert sandbox.context["result_list"] == [0, 1, 1, 2, 3, 5, 8, 13]


def test_import_and_use_module():
    sandbox = Sandbox()
    # Step 1: Import a module
    result1 = sandbox.run("import math")
    assert result1["success"]
    assert "math" in sandbox.context

    # Step 2: Use the imported module
    result2 = sandbox.run("radius = 5; area = math.pi * radius**2")
    assert result2["success"]
    assert sandbox.context["area"] == 78.53981633974483


def test_define_and_instantiate_class():
    sandbox = Sandbox()
    # Step 1: Define a class
    class_def_code = """
class Greeter:
    def __init__(self, name):
        self.name = name
    def greet(self):
        return f"Hello, {self.name}!"
"""
    result1 = sandbox.run(class_def_code)
    assert result1["success"]
    assert "Greeter" in sandbox.context

    # Step 2: Instantiate and use the class
    class_use_code = """
greeter_instance = Greeter("World")
message = greeter_instance.greet()
"""
    result2 = sandbox.run(class_use_code)
    assert result2["success"]
    assert sandbox.context["message"] == "Hello, World!"


def test_modify_mutable_object_in_context():
    sandbox = Sandbox()
    sandbox.context = {"my_list": [1, 2]}
    # Append to the list
    result = sandbox.run("my_list.append(3)")
    assert result["success"]
    assert sandbox.context["my_list"] == [1, 2, 3]


def test_handle_syntax_error():
    sandbox = Sandbox()
    code = "for i in range(5)"  # Missing colon
    result = sandbox.run(code)
    assert not result["success"]
    assert "SyntaxError" in result["stderr"]


def test_lack_of_isolation_filesystem_access():
    # This test demonstrates that the sandbox is NOT isolated and can interact
    # with the filesystem, which can be a security risk.
    sandbox = Sandbox()
    # This code will list the files in the current directory
    code = "import os; files = os.listdir('.')"
    result = sandbox.run(code)
    assert result["success"]
    # Check that the 'files' variable in the context is a list (of filenames)
    assert isinstance(sandbox.context["files"], list)
    # Check that a known file from the project root is listed
    assert "pyproject.toml" in sandbox.context["files"]


def test_reset_context():
    sandbox = Sandbox()
    sandbox.run("x = 10")
    assert sandbox.context == {"x": 10}
    sandbox.reset()
    assert sandbox.context == {}


def test_get_context():
    sandbox = Sandbox()
    sandbox.run("a = 1; b = 'hello'")
    context = sandbox.get_context()
    assert context == {"a": 1, "b": "hello"}
    # Verify it's a copy by modifying it and checking the original
    context["c"] = 3
    assert sandbox.context == {"a": 1, "b": "hello"}


@pytest.mark.asyncio
async def test_arun_simple_execution():
    sandbox = Sandbox()
    code = "x = 10; y = x + 5"
    result = await sandbox.arun(code)
    assert result["success"]
    assert sandbox.get_context() == {"x": 10, "y": 15}


@pytest.mark.asyncio
async def test_arun_supports_await():
    sandbox = Sandbox()
    code = "import asyncio\nawait asyncio.sleep(0.01)\nx = 10"
    result = await sandbox.arun(code)
    assert result["success"]
    assert "x" in sandbox.get_context()
    assert sandbox.get_context()["x"] == 10


@pytest.mark.asyncio
async def test_arun_maintains_context():
    sandbox = Sandbox()
    sandbox.run("y = 5")
    code = "import asyncio\nx = y + 5\nawait asyncio.sleep(0.01)\nz = x + 1"
    result = await sandbox.arun(code)
    assert result["success"]
    context = sandbox.get_context()
    assert context.get("y") == 5
    assert context.get("x") == 10
    assert context.get("z") == 11


@pytest.mark.asyncio
async def test_arun_await_handles_errors():
    sandbox = Sandbox()
    code = "import asyncio\nawait asyncio.sleep(0.01)\n1 / 0"
    result = await sandbox.arun(code)
    assert not result["success"]
    assert "ZeroDivisionError" in result["stderr"]


@pytest.mark.asyncio
async def test_arun_supports_sync_code():
    sandbox = Sandbox()
    # Step 1: Define the Fibonacci generator function (synchronous code)
    fib_def_code = """
def fibonacci(n):
    a, b = 0, 1
    for _ in range(n):
        yield a
        a, b = b, a + b
"""
    result1 = await sandbox.arun(fib_def_code)
    assert result1["success"]
    assert "fibonacci" in sandbox.context

    # Step 2: Call the generator (also synchronous)
    fib_call_code = """
fib_gen = fibonacci(8)
result_list = list(fib_gen)
print(result_list)
"""
    result2 = await sandbox.arun(fib_call_code)
    assert result2["success"]
    assert result2["stdout"].strip() == "[0, 1, 1, 2, 3, 5, 8, 13]"
    assert sandbox.context["result_list"] == [0, 1, 1, 2, 3, 5, 8, 13]
