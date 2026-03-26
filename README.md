# QA-PayTest 支付测试自动化框架

## 项目概述

本项目是支付模块的自动化测试框架，支持多种支付场景的测试，包括金豆支付、金币支付、商城购买、房间支付等。

## 项目结构

```
qa-payTest/
├── case/              # 测试用例
├── caseOversea/       # 海外版测试用例
├── caseSlp/           # slp平台测试用例
├── caseStarify/       # Starify平台测试用例
├── caseGames/         # 游戏平台测试用例
├── caseLuckyPlay/     # 玩法测试用例
├── common/            # 公共模块
├── common/            # 核心公共类
└── requirements.txt   # 依赖配置
```

## 核心模块说明

### Common类设计

| 模块 | 功能说明 |
|------|----------|
| `Request.py` | 封装HTTP请求方法，支持GET/POST/PUT等多协议扩展 |
| `Config.py` | 配置管理，包含环境配置、数据路径等 |
| `paramsYaml.py` | YAML配置文件读取器 |
| `Logs.py` | 日志记录，支持debug/info/warning/error/critical级别 |
| `Session.py` | 登录Token获取与管理 |
| `sqlScript.py` | SQL脚本执行 |
| `conMysql.py` | MySQL数据库连接与操作 |
| `conRedis.py` | Redis连接与操作 |
| `Assert.py` | 断言验证工具 |
| `Consts.py` | 全局数据记录 |
| `HTMLTestRunner.py` | HTML测试报告生成 |
| `runFailed.py` | 失败重试机制 |
| `basicData.py` | 数据编码处理 |

## 测试规范

### 文件命名规范
- 测试文件以 `test_` 开头
- 测试类以 `Test` 开头，且不能带有 `__init__` 方法
- 测试函数以 `test_` 开头

### 代码规范
- 类名语义化，如 `TestPayOpenBox`、`TestPayShopBuy`
- 提取公共方法 `_prepare_test_data` 和 `_validate_db_state`
- 测试流程结构化：准备 → 请求 → 响应验证 → 数据库验证 → 记录

## 快速开始

### 环境安装

```bash
# 安装依赖
pip install -r requirements.txt

# 或单独安装GitPython
pip install gitpython
```

### 运行测试

```bash
# 运行所有测试
python run_all_case.py

# 运行定时任务
python run_crontab_case.py

# 运行并发测试
python testConcurrent.py
```

## 配置说明

配置文件位于 `common/Config.py`，包含：
- 环境配置（dev/test/prod）
- 数据库连接配置
- Redis连接配置
- 应用信息配置

## 测试用例分类

| 目录 | 说明 |
|------|------|
| `case/` | 核心支付测试 |
| `caseOversea/` | 海外多区域测试 |
| `caseSlp/` | slp平台测试 |
| `caseStarify/` | Starify平台测试 |
| `caseGames/` | 游戏相关支付测试 |
| `caseLuckyPlay/` | 各类玩法测试 |

## 注意事项

1. 运行测试前请确保配置文件正确
2. 数据库连接需要正确的权限
3. 并发测试会占用较多资源，请谨慎使用
