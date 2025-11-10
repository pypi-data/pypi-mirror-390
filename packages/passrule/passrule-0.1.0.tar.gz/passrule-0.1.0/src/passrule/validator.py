"""密码校验器实现"""

import re
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class ValidationRule:
    """密码校验规则配置"""
    min_length: int = 8
    max_length: Optional[int] = None
    require_digits: bool = True
    require_uppercase: bool = True
    require_lowercase: bool = True
    require_special_chars: bool = True
    special_chars: str = "!@#$%^&*()_+-=[]{}|;:,.<>?"


class PasswordValidator:
    """密码校验器"""
    
    def __init__(self, rule: ValidationRule = None):
        self.rule = rule or ValidationRule()
    
    def validate(self, password: str) -> tuple[bool, List[str]]:
        """
        校验密码
        
        Args:
            password: 待校验的密码
            
        Returns:
            tuple: (是否通过校验, 错误信息列表)
        """
        errors = []
        
        # 检查长度
        if len(password) < self.rule.min_length:
            errors.append(f"密码长度不能少于{self.rule.min_length}位")
        
        if self.rule.max_length and len(password) > self.rule.max_length:
            errors.append(f"密码长度不能超过{self.rule.max_length}位")
        
        # 检查数字
        if self.rule.require_digits and not re.search(r'\d', password):
            errors.append("密码必须包含数字")
        
        # 检查大写字母
        if self.rule.require_uppercase and not re.search(r'[A-Z]', password):
            errors.append("密码必须包含大写字母")
        
        # 检查小写字母
        if self.rule.require_lowercase and not re.search(r'[a-z]', password):
            errors.append("密码必须包含小写字母")
        
        # 检查特殊字符
        if self.rule.require_special_chars:
            special_pattern = f"[{re.escape(self.rule.special_chars)}]"
            if not re.search(special_pattern, password):
                errors.append("密码必须包含特殊字符")
        
        return len(errors) == 0, errors
    
    def is_valid(self, password: str) -> bool:
        """简单校验，只返回是否通过"""
        valid, _ = self.validate(password)
        return valid