# Test Case Converter

Convert test cases between Excel and XMind formats.

## Installation
```bash
pip install testcase-converter
```

## New Features in v0.4.0

- Added functionality to split XMind files by specified row count
- Added case type field with default value "功能用例"
- Reordered XMind notes fields to match required sequence
- Enhanced compatibility for both old and new Excel formats

## Usage Examples

### As a CLI Tool:
```bash
# Excel to XMind
testcase-converter test_cases.xlsx

# XMind to Excel
testcase-converter test_cases.xmind

# 启用日志文件生成（使用简短参数 -l）
testcase-converter -l test_cases.xlsx

# 设置默认车型和优先级（使用简短参数 -v 和 -p）
testcase-converter -v "默认车型" -p "3" test_cases.xlsx

# 仅填充模式（使用简短参数 -f）
testcase-converter -f -v "OTA" -p "0" test_cases.xlsx

# 按指定行数分割生成多个XMind文件（使用简短参数 -r）
testcase-converter -r 100 test_cases.xlsx

# 组合使用所有参数
testcase-converter -l -f -v "OTA" -p "0" -r 50 test_cases.xlsx
```

### As a Python Library:
```python
from testcase_converter import TestCaseConverter, ConversionType

# Auto-detect conversion type
converter = TestCaseConverter("input.xlsx")
converter.convert()

# Explicitly specify conversion type with new options
converter = TestCaseConverter(
    "input.xmind", 
    ConversionType.XMIND_TO_EXCEL,
    enable_logging=True,              # 启用日志文件生成
    default_vehicle_type="默认车型",      # 设置默认车型
    default_priority="3",             # 设置默认优先级
    rows_per_xmind=100                # 每个XMind文件包含100行
)

# 仅填充模式
converter = TestCaseConverter(
    "input.xlsx",
    ConversionType.FILL_ONLY,         # 设置为仅填充模式
    default_vehicle_type="OTA",       # 设置默认车型
    default_priority="0"              # 设置默认优先级
)
converter.convert()
```

### 命令行参数说明

| 长参数名 | 短参数名 | 说明 |
|---------|---------|------|
| `--enable-logging` | `-l` | 启用日志文件生成 |
| `--default-vehicle-type` | `-v` | 默认车型，用于填充空的车型字段 |
| `--default-priority` | `-p` | 默认优先级，用于填充空的优先级字段 |
| `--fill-only` | `-f` | 仅填充模式，不转换文件格式 |
| `--rows-per-xmind` | `-r` | 每个XMind文件包含的行数 |
| `--debug` | 无 | 启用调试模式 |

### Format Details

The converter now automatically adds a case type field with the default value "功能用例" and reorders the fields in XMind notes.

For Excel files:
- New format includes 9 columns: Module, Case Name, Precondition, Steps, Expected Result, Remark, Case Type, Vehicle Type, Priority
- Backward compatibility maintained for 7-column and 8-column formats (missing fields will be added with default values)

For XMind files:
- Fields are now ordered as follows:
  【用例类型】功能用例
  【车型】OTA
  【优先级】1
  【前置条件】
  【执行步骤】
  【预期结果】
  【备注】