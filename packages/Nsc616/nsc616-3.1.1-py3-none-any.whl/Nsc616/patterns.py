"""
模式定义函数
"""

from typing import Any

def string(value: str) -> dict:
    """固定字符串模式"""
    return {"type": "string", "value": value}

def r_input(var_name: str) -> dict:
    """输入变量模式"""
    return {"type": "input", "var": var_name}

def optional(pattern: Any) -> dict:
    """可选模式"""
    return {"type": "optional", "pattern": pattern}

def endl() -> dict:
    """换行符模式"""
    return {"type": "endl"}

def any_of(*patterns: Any) -> dict:
    """多选一模式"""
    return {"type": "any_of", "patterns": patterns}

def sequence(*patterns: Any) -> dict:
    """序列模式"""
    return {"type": "sequence", "patterns": patterns}