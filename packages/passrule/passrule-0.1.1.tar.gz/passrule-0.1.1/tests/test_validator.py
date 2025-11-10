"""密码校验器测试"""

import pytest
from passrule import PasswordValidator, ValidationRule


class TestPasswordValidator:
    
    def test_default_rule_valid_password(self):
        validator = PasswordValidator()
        is_valid, errors = validator.validate("MyPassword123!")
        assert is_valid
        assert len(errors) == 0
    
    def test_default_rule_invalid_password(self):
        validator = PasswordValidator()
        is_valid, errors = validator.validate("weak")
        assert not is_valid
        assert len(errors) > 0
    
    def test_custom_rule(self):
        rule = ValidationRule(
            min_length=6,
            require_uppercase=False,
            require_special_chars=False
        )
        validator = PasswordValidator(rule)
        is_valid, errors = validator.validate("password123")
        assert is_valid
        assert len(errors) == 0
    
    def test_length_validation(self):
        rule = ValidationRule(min_length=10, max_length=15)
        validator = PasswordValidator(rule)
        
        # 太短
        is_valid, errors = validator.validate("short")
        assert not is_valid
        assert "密码长度不能少于10位" in errors
        
        # 太长
        is_valid, errors = validator.validate("verylongpassword123!")
        assert not is_valid
        assert "密码长度不能超过15位" in errors
    
    def test_is_valid_method(self):
        validator = PasswordValidator()
        assert validator.is_valid("MyPassword123!")
        assert not validator.is_valid("weak")