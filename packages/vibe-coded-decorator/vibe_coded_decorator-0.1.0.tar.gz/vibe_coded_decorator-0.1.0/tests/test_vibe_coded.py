"""Tests for the vibe_coded decorator."""

import pytest
from vibe_coded_decorator import vibe_coded


def test_decorator_with_existing_docstring():
    """Test that decorator prepends notice to existing docstring."""
    @vibe_coded
    def test_func():
        """Original docstring."""
        return "test"
    
    assert test_func.__doc__ == "**THIS FUNCTION HAS BEEN VIBE CODED**\n\nOriginal docstring."
    assert test_func() == "test"


def test_decorator_without_docstring():
    """Test that decorator adds notice when no docstring exists."""
    @vibe_coded
    def test_func():
        return "test"
    
    assert test_func.__doc__ == "**THIS FUNCTION HAS BEEN VIBE CODED**"
    assert test_func() == "test"


def test_decorator_preserves_function_metadata():
    """Test that decorator preserves function name and other metadata."""
    @vibe_coded
    def original_function_name():
        """Test function."""
        return "test"
    
    assert original_function_name.__name__ == "original_function_name"
    assert callable(original_function_name)


def test_decorator_with_arguments():
    """Test that decorator works with functions that have arguments."""
    @vibe_coded
    def test_func(arg1, arg2, kwarg1=None):
        """Function with arguments."""
        return arg1 + arg2 + (kwarg1 or 0)
    
    assert test_func.__doc__.startswith("**THIS FUNCTION HAS BEEN VIBE CODED**")
    assert test_func(1, 2, kwarg1=3) == 6
    assert test_func(1, 2) == 3


def test_decorator_with_multiline_docstring():
    """Test that decorator works with multiline docstrings."""
    @vibe_coded
    def test_func():
        """This is a multiline docstring.
        
        It has multiple lines.
        And more information here.
        """
        return "test"
    
    docstring = test_func.__doc__
    assert docstring.startswith("**THIS FUNCTION HAS BEEN VIBE CODED**")
    assert "This is a multiline docstring" in docstring
    assert "It has multiple lines" in docstring
    assert "And more information here" in docstring


def test_decorator_with_empty_docstring():
    """Test that decorator handles empty docstring."""
    @vibe_coded
    def test_func():
        """"""
        return "test"
    
    # Empty docstring is falsy, so it should just have the notice
    assert test_func.__doc__ == "**THIS FUNCTION HAS BEEN VIBE CODED**"


def test_decorator_with_whitespace_only_docstring():
    """Test that decorator handles whitespace-only docstring."""
    @vibe_coded
    def test_func():
        """   """
        return "test"
    
    # Whitespace-only docstring is truthy, so it should prepend
    assert test_func.__doc__.startswith("**THIS FUNCTION HAS BEEN VIBE CODED**")
    assert "   " in test_func.__doc__


def test_decorator_on_class_method():
    """Test that decorator works on class methods."""
    class TestClass:
        @vibe_coded
        def method(self):
            """A class method."""
            return "method_result"
        
        @classmethod
        @vibe_coded
        def class_method(cls):
            """A classmethod."""
            return "class_method_result"
        
        @staticmethod
        @vibe_coded
        def static_method():
            """A static method."""
            return "static_method_result"
    
    instance = TestClass()
    
    # Test instance method
    assert instance.method.__doc__.startswith("**THIS FUNCTION HAS BEEN VIBE CODED**")
    assert instance.method() == "method_result"
    
    # Test classmethod (decorator order: @classmethod then @vibe_coded)
    assert TestClass.class_method.__doc__.startswith("**THIS FUNCTION HAS BEEN VIBE CODED**")
    assert TestClass.class_method() == "class_method_result"
    
    # Test staticmethod (decorator order: @staticmethod then @vibe_coded)
    assert TestClass.static_method.__doc__.startswith("**THIS FUNCTION HAS BEEN VIBE CODED**")
    assert TestClass.static_method() == "static_method_result"


def test_decorator_on_async_function():
    """Test that decorator works on async functions."""
    @vibe_coded
    async def async_func():
        """An async function."""
        return "async_result"
    
    assert async_func.__doc__.startswith("**THIS FUNCTION HAS BEEN VIBE CODED**")
    assert "An async function" in async_func.__doc__


def test_decorator_preserves_function_signature():
    """Test that decorator preserves function signature for introspection."""
    @vibe_coded
    def test_func(a, b, c=10, *args, **kwargs):
        """Function with complex signature."""
        return a + b + c
    
    import inspect
    sig = inspect.signature(test_func)
    params = list(sig.parameters.keys())
    
    assert params == ['a', 'b', 'c', 'args', 'kwargs']
    assert test_func(1, 2) == 13
    assert test_func(1, 2, 3) == 6


def test_decorator_notice_format():
    """Test that the notice has the exact expected format."""
    @vibe_coded
    def test_func():
        """Test."""
        pass
    
    expected_notice = "**THIS FUNCTION HAS BEEN VIBE CODED**"
    assert test_func.__doc__.startswith(expected_notice)
    assert test_func.__doc__ == f"{expected_notice}\n\nTest."


def test_multiple_decorators():
    """Test that decorator can be combined with other decorators."""
    def other_decorator(func):
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs) * 2
        return wrapper
    
    @vibe_coded
    @other_decorator
    def test_func():
        """Test function."""
        return 5
    
    assert test_func.__doc__.startswith("**THIS FUNCTION HAS BEEN VIBE CODED**")
    assert test_func() == 10


def test_decorator_on_lambda():
    """Test that decorator works on lambda functions (though unusual)."""
    # Note: Lambdas typically don't have docstrings, but we can test the behavior
    test_lambda = vibe_coded(lambda x: x * 2)
    
    assert test_lambda.__doc__ == "**THIS FUNCTION HAS BEEN VIBE CODED**"
    assert test_lambda(5) == 10

