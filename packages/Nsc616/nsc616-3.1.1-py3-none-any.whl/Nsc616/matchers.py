"""
模式匹配器实现
"""

from typing import List, Tuple, Any, Optional
from .exceptions import PatternMatchError

class BaseMatcher:
    """基础匹配器"""
    def match(self, tokens: List[str], start_index: int) -> Tuple[Any, int]:
        raise NotImplementedError
    
    def is_optional(self) -> bool:
        return False
    
    def extracts_argument(self) -> bool:
        return False

class StringMatcher(BaseMatcher):
    """字符串匹配器"""
    def __init__(self, pattern_def: dict):
        self.value = pattern_def["value"]
    
    def match(self, tokens: List[str], start_index: int) -> Tuple[Any, int]:
        if start_index < len(tokens) and tokens[start_index] == self.value:
            return None, 1  # 匹配成功，但不提取参数
        return None, 0  # 不匹配

class InputMatcher(BaseMatcher):
    """输入变量匹配器"""
    def __init__(self, pattern_def: dict):
        self.var_name = pattern_def["var"]
    
    def match(self, tokens: List[str], start_index: int) -> Tuple[Any, int]:
        if start_index < len(tokens):
            return tokens[start_index], 1
        return None, 0
    
    def extracts_argument(self) -> bool:
        return True

class OptionalMatcher(BaseMatcher):
    """可选模式匹配器"""
    def __init__(self, pattern_def: dict):
        from .core import create_matcher
        self.inner_matcher = create_matcher(pattern_def["pattern"])
    
    def match(self, tokens: List[str], start_index: int) -> Tuple[Any, int]:
        result, consumed = self.inner_matcher.match(tokens, start_index)
        if result is not None:
            return result, consumed
        return None, 0  # 可选模式不匹配也没关系
    
    def is_optional(self) -> bool:
        return True
    
    def extracts_argument(self) -> bool:
        return self.inner_matcher.extracts_argument()

class EndlMatcher(BaseMatcher):
    """换行符匹配器"""
    def match(self, tokens: List[str], start_index: int) -> Tuple[Any, int]:
        # 换行符在令牌化时可能已经处理
        return None, 0

def create_matcher(pattern_def: Any) -> BaseMatcher:
    """创建对应的匹配器"""
    if isinstance(pattern_def, dict):
        matcher_type = pattern_def.get("type")
        if matcher_type == "string":
            return StringMatcher(pattern_def)
        elif matcher_type == "input":
            return InputMatcher(pattern_def)
        elif matcher_type == "optional":
            return OptionalMatcher(pattern_def)
        elif matcher_type == "endl":
            return EndlMatcher(pattern_def)
    
    raise ValueError(f"未知的模式类型: {pattern_def}")
