"""使用示例"""

from passrule import PasswordValidator, ValidationRule


def main():
    # 默认规则示例
    print("=== 默认规则测试 ===")
    validator = PasswordValidator()
    
    passwords = ["MyPassword123!", "weak", "NoSpecial123", "nodigits!"]
    
    for pwd in passwords:
        is_valid, errors = validator.validate(pwd)
        print(f"密码: {pwd}")
        print(f"有效: {is_valid}")
        if errors:
            print(f"错误: {', '.join(errors)}")
        print()
    
    # 自定义规则示例
    print("=== 自定义规则测试 ===")
    rule = ValidationRule(
        min_length=6,
        max_length=20,
        require_uppercase=False,
        require_special_chars=False
    )
    
    custom_validator = PasswordValidator(rule)
    
    test_passwords = ["password123", "short", "verylongpasswordthatexceedslimit"]
    
    for pwd in test_passwords:
        is_valid, errors = custom_validator.validate(pwd)
        print(f"密码: {pwd}")
        print(f"有效: {is_valid}")
        if errors:
            print(f"错误: {', '.join(errors)}")
        print()


if __name__ == "__main__":
    main()