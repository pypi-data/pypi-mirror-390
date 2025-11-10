"""
Nsc616 异常类
"""

class PatternMatchError(Exception):
    """模式匹配错误"""
    
    def __init__(self, message, input_text=None, patterns=None, position=None):
        self.message = message
        self.input_text = input_text
        self.patterns = patterns
        self.position = position
        super().__init__(self._format_message())
    
    def _format_message(self):
        msg = f"模式匹配错误: {self.message}"
        if self.input_text:
            msg += f"\n输入文本: '{self.input_text}'"
        if self.position is not None and self.input_text:
            msg += f"\n错误位置: {' ' * self.position}^"
        if self.patterns:
            msg += f"\n期望模式: {[str(p) for p in self.patterns]}"
        return msg

class SyntaxError(Exception):
    """语法错误"""
    
    def __init__(self, message, line=None, column=None, code_snippet=None):
        self.message = message
        self.line = line
        self.column = column
        self.code_snippet = code_snippet
        super().__init__(self._format_message())
    
    def _format_message(self):
        msg = f"语法错误: {self.message}"
        if self.line is not None:
            msg += f" (第{self.line}行"
            if self.column is not None:
                msg += f", 第{self.column}列"
            msg += ")"
        if self.code_snippet:
            msg += f"\n代码片段: {self.code_snippet}"
        return msg

class ValidationError(Exception):
    """验证错误"""
    
    def __init__(self, message, value=None, expected_type=None):
        self.message = message
        self.value = value
        self.expected_type = expected_type
        super().__init__(self._format_message())
    
    def _format_message(self):
        msg = f"验证错误: {self.message}"
        if self.value is not None:
            msg += f"\n输入值: {repr(self.value)}"
        if self.expected_type:
            msg += f"\n期望类型: {self.expected_type}"
        return msg

# 使用示例
if __name__ == "__main__":
    try:
        raise PatternMatchError(
            "缺少必需的参数",
            input_text="print",
            patterns=["print", "<message>"],
            position=5
        )
    except PatternMatchError as e:
        print(e)
    
    print("\n" + "="*50 + "\n")
    
    try:
        raise SyntaxError(
            "未闭合的引号",
            line=3,
            column=15,
            code_snippet='print("hello world)'
        )
    except SyntaxError as e:
        print(e)