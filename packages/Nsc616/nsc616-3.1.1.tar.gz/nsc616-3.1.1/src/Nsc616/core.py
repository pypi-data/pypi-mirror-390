"""
Nsc616 核心模式匹配引擎
"""

import re
from typing import Any, List, Tuple, Callable, Union
from .exceptions import PatternMatchError
from .matchers import create_matcher

class Pattern:
    """模式基类"""
    def __init__(self, pattern_def):
        self.pattern_def = pattern_def
        self.matcher = create_matcher(pattern_def)

def expr_format(*patterns):
    """
    主装饰器：将输入文本按照模式解析为参数
    """
    def decorator(func: Callable) -> Callable:
        def wrapper(input_text: str, *args, **kwargs) -> Any:
            if isinstance(input_text, str):
                # 创建模式匹配器
                matchers = [create_matcher(pattern) for pattern in patterns]
                
                # 执行模式匹配
                success, extracted_args = _match_patterns(matchers, input_text)
                
                if success:
                    return func(*extracted_args, *args, **kwargs)
                else:
                    raise PatternMatchError(f"无法匹配模式: {input_text}")
            else:
                return func(input_text, *args, **kwargs)
        
        wrapper._nsc616_patterns = patterns  # 保存模式信息用于调试
        return wrapper
    return decorator

def match(patterns: List, input_text: str) -> Tuple[bool, List]:
    """
    直接模式匹配函数
    """
    matchers = [create_matcher(pattern) for pattern in patterns]
    return _match_patterns(matchers, input_text)

def _match_patterns(matchers: List, input_text: str) -> Tuple[bool, List]:
    """
    执行模式匹配
    """
    tokens = _tokenize(input_text)
    token_index = 0
    extracted_args = []
    
    for matcher in matchers:
        if token_index >= len(tokens):
            if matcher.is_optional():
                continue
            else:
                return False, []
        
        result, consumed = matcher.match(tokens, token_index)
        if result is not None:
            if matcher.extracts_argument():
                extracted_args.append(result)
            token_index += consumed
        elif not matcher.is_optional():
            return False, []
    
    return True, extracted_args

def _tokenize(text: str) -> List[str]:
    """
    将输入文本令牌化
    """
    # 简单的空格分割，支持引号内的字符串
    tokens = []
    current = ""
    in_quotes = False
    quote_char = None
    escape = False
    
    for char in text:
        if escape:
            current += char
            escape = False
        elif char == '\\':
            escape = True
        elif char in ('"', "'") and not in_quotes:
            in_quotes = True
            quote_char = char
            current += char
        elif char == quote_char and in_quotes:
            in_quotes = False
            current += char
            tokens.append(current)
            current = ""
        elif char == ' ' and not in_quotes:
            if current:
                tokens.append(current)
                current = ""
        else:
            current += char
    
    if current:
        tokens.append(current)
    
    return tokens
