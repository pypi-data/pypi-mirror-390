"""
Nsc616 - 强大的模式匹配和表达式解析库
"""

from .core import expr_format, match, Pattern
from .patterns import string, r_input, optional, endl, any_of, sequence
from .matchers import StringMatcher, InputMatcher, OptionalMatcher
from .exceptions import PatternMatchError, SyntaxError

__version__ = "1.0.0"
__all__ = [
    'expr_format', 'match', 'Pattern',
    'string', 'r_input', 'optional', 'endl', 'any_of', 'sequence',
    'StringMatcher', 'InputMatcher', 'OptionalMatcher',
    'PatternMatchError', 'SyntaxError'
]