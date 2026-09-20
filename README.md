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
├── common/            # 公共模块与核心类（请求/配置/日志/数据库/Session）
├── tests/             # 公共模块离线单元测试（无需后端）
├── .github/workflows/ # CI 流水线（离线检查）
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
| `runFailed.py` | 失败重试机制 |
| `basicData.py` | 数据编码处理 |
| `scene_base.py` | 场景执行骨架（七段式模板方法，供各域测试基类复用） |

## 测试规范

### 文件命名规范
- 测试文件以 `test_` 开头
- 测试类以 `Test` 开头，且不能带有 `__init__` 方法
- 测试函数以 `test_` 开头

### 代码规范
- 类名语义化，如 `TestPayOpenBox`、`TestPayShopBuy`
- 提取公共方法 `_prepare_test_data` 和 `_validate_db_state`
- 测试流程结构化：准备 → 请求 → 响应验证 → 数据库验证 → 记录

### 数据驱动用例（SCENES 表）

- `case/`、`caseOversea/`、`caseSlp/`、`caseStarify/` 等目录的用例已数据驱动化：每个测试文件在模块级声明 `SCENES` 表，一个场景只声明与基准场景的差异点
- 场景字段：`des`（描述兼报告键）、`setup`、`data`、`checks`、`success`、`msg`、`post_wait`、`queries`、`prepare`、`report`
- `data` 与 `checks.expected` 支持 `callable(ctx)` 延迟求值（`ctx` 含 `queries` 查询结果与测试类引用）

### 场景执行骨架（common/scene_base.py）

- `SceneFlowBase.run_flow(scene)` 统一编排七个阶段：准备 → 查询 → 请求 → 断言 → 等待 → 校验 → 记录；阶段间通过共享 `ctx`（初始含 `cls`/`self`）传递中间状态
- 域基类为薄适配层，仅实现 `flow_*` 钩子：
  - `case/base.py` 的 `PayTestBase`（`PayCase` + `run_case`），`_prepare_test_data` / `_validate_db_state` 步骤分发器保留在本模块
  - `caseOversea/base.py` 的 `OverseaTestBase`（公共前置处理：礼物配置检查/用户大区/房间大区/Redis 清理），下分 `OverseaAreaTestBase`（`PayScene` + `run_scene`，区域消费差异化场景）与 `OverseaBizTestBase`（`OverseaBizCase` + `run_case`，通用支付业务场景）两个分支
  - `caseSlp/base.py` 的 `SlpTestBase`（`SlpCase` + `run_case`），域步骤/校验分发器与报告表路由（`case_list` / `case_list_b`）在本模块
  - `caseStarify/base.py` 的 `StarifyTestBase`（`StarifyCase` + `run_case`），失败用例以 `success=None` 仅断言 `msg`，`checks` 为无参断言函数列表
- 兼容别名：模块级 `_resolve`、`PayTestBase._resolve_check`、`REPORT_TABLES`、`case_list` 引用均保留在原文件，子类与测试的 patch/引用目标不变

### 测试数据夹具约定

共享测试实体（用户 UID、房间号、礼物/商品 ID）集中声明，禁止在用例中散落硬编码数字：

| 域 | 夹具模块 | 说明 |
|----|----------|------|
| 主站（BB）+ 海外版 | `common/Config.py` | `bb_user` / `live_role` / `oversea_user` / `oversea_room` / `giftId` / `oversea_giftId` / `commodity` 等子配置，经 `config` 单例访问 |
| SLP | `caseSlp/config.py` | SLP 用户体系独立维护，不合并进 common/Config.py |
| Starify | `caseStarify/need_data.py` | Starify 实体与作品/礼物数据集独立维护 |

- 新增场景实体优先在对应域夹具模块声明；跨域通用实体（如 `giftId`）才收敛到 `common/Config.py`
- `tests/test_config.py` 锁定主站/海外夹具的关键取值与结构（含 `giftId` 键集合），任何静默改数据都会使测试失败

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

### 离线自测（无需后端环境）

```bash
# 公共模块单元测试（tests/，全程 mock，不依赖后端/数据库）
python -m pytest tests/ -q

# 用例收集基线校验（防止用例文件损坏或误删导致覆盖静默下降）
python check_collect.py
```

以上检查已在 CI（`.github/workflows/ci.yml`）中自动执行。

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
