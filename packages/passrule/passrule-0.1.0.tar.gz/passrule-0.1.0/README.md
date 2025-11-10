# PassRule

可配置的密码校验库，支持自定义校验规则。

## 安装

```bash
pip install passrule
```

## 使用方法

### 基本使用

```python
from passrule import PasswordValidator

# 使用默认规则
validator = PasswordValidator()
is_valid, errors = validator.validate("MyPassword123!")
print(is_valid)  # True
print(errors)    # []
```

### 自定义规则

```python
from passrule import PasswordValidator, ValidationRule

# 自定义规则
rule = ValidationRule(
    min_length=6,
    max_length=20,
    require_digits=True,
    require_uppercase=False,
    require_lowercase=True,
    require_special_chars=True,
    special_chars="!@#$%"
)

validator = PasswordValidator(rule)
is_valid, errors = validator.validate("password123!")
```

## 校验规则

- `min_length`: 最小长度（默认8）
- `max_length`: 最大长度（默认无限制）
- `require_digits`: 是否需要数字（默认True）
- `require_uppercase`: 是否需要大写字母（默认True）
- `require_lowercase`: 是否需要小写字母（默认True）
- `require_special_chars`: 是否需要特殊字符（默认True）
- `special_chars`: 允许的特殊字符（默认"!@#$%^&*()_+-=[]{}|;:,.<>?"）

## 许可证

MIT