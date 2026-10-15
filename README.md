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
├── docs/              # 文档与设计资料（tdr 表设计图等）
├── others/            # 独立辅助脚本（点餐 bot、环境配置参考），不进 CI 主链
├── probabilityTest/   # 概率类独立验证脚本，不进 pytest 收集基线
├── .github/workflows/ # CI 流水线（离线检查）
└── requirements.txt   # 依赖配置（核心 7 包钉 CI 同款版本 + 可选段）
```

## 核心模块说明

### Common类设计

| 模块 | 功能说明 |
|------|----------|
| `request_util.py` | 封装HTTP请求方法，支持GET/POST/PUT等多协议扩展 |
| `config.py` | 配置管理，包含环境配置、数据路径等 |
| `params_yaml.py` | YAML配置文件读取器 |
| `logs.py` | 日志记录，支持debug/info/warning/error/critical级别 |
| `session.py` | 登录Token获取与管理 |
| `sql_script.py` | SQL脚本执行 |
| `con_mysql.py` | MySQL数据库连接与操作 |
| `con_redis.py` | Redis连接与操作 |
| `assert_util.py` | 断言验证工具 |
| `consts.py` | 全局数据记录 |
| `run_failed.py` | 失败重试机制 |
| `basic_data.py` | 数据编码处理 |
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
- `data` 与 `checks.expected` 支持 `callable(ctx)` 延迟求值（`ctx` 含 `queries` 查询结果与测试类引用）

以主站 `PayCase` 为例，各字段语义（其余域的 Case 字段以对应 `base.py` 为准）：

| 字段 | 类型 | 说明 |
|------|------|------|
| `des` | str | 场景描述，兼作结果报告表的键 |
| `setup` | list | 数据准备步骤（`_prepare_test_data` 分发格式） |
| `queries` | list | 请求前查询 `(ctx 键, 无参可调用)`，结果存入 `ctx` |
| `data` | dict | `encodeData` 入参；值可为 `callable(ctx)` 运行期求值 |
| `success` / `msg` | int / str | 响应断言（`success` 默认 1；`msg=None` 时跳过断言） |
| `post_wait` | float | 请求后等待秒数（等 NSQ 等异步消息处理） |
| `checks` | list | DB 校验项；`expected` 可为 `callable(ctx)` 延迟求值 |
| `prepare` | callable | 自定义组合准备 `callable(testcase)`，先于 `setup` 执行 |
| `report` | str | 结果记录表：`case_list` / `case_list_b` / `case_list_c` |

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
| 主站（BB）+ 海外版 | `common/config.py` | `bb_user` / `live_role` / `oversea_user` / `oversea_room` / `giftId` / `oversea_giftId` / `commodity` 等子配置，经 `config` 单例访问 |
| SLP | `caseSlp/config.py` | SLP 用户体系独立维护，不合并进 common/config.py |
| Starify | `caseStarify/need_data.py` | Starify 实体与作品/礼物数据集独立维护 |

- 新增场景实体优先在对应域夹具模块声明；跨域通用实体（如 `giftId`）才收敛到 `common/config.py`
- `tests/test_config.py` 锁定主站/海外夹具的关键取值与结构（含 `giftId` 键集合），任何静默改数据都会使测试失败

### 新增用例指引

以主站为例（其余域替换对应基类与夹具模块）：

1. 在域夹具模块（主站为 `common/config.py`）声明新实体（用户/房间/礼物/商品 ID），禁止在用例中硬编码数字
2. 在对应测试文件的模块级 `SCENES` 表追加场景，只写与基准场景的差异字段，无需新增测试方法
3. 若涉及新支付类型：在 `common/basic_data.py` 的 `PAY_TYPE_HANDLERS`（或 `basic_slp_data.py` 等域编码模块）注册 handler，并同步补 `tests/` 下对应单测
4. 用例数量变化后同步 `check_collect.py` 的 `EXPECTED_COLLECT_COUNT` 基线，防止覆盖静默下降

## 快速开始

### 环境安装

```bash
# Python 3.11（与 CI 同款解释器版本）
pip install -r requirements.txt
```

依赖分两段：核心 7 包（pytest/requests/urllib3/PyMySQL/gevent/PyYAML/redis）钉定 CI 同款版本，保证本地与 CI 行为一致、可离线复现；可选段（chinesecalendar、GitPython）仅被独立脚本使用，缺失不影响 pytest 主链。

内网数据库/Redis 地址已支持环境变量覆盖（如 `DB_DEV_HOST`、`DB_ALI_HOST`、`DB_RDS_HOST`、`REDIS_46_HOST`、`BB_STARIFY_HOST`、`BB_SLP_HOST`、`BB_RUSH_HOST`），默认值不变，切换环境无需改代码。

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

## CI/CD 流水线

项目配置了 GitHub Actions 自动流水线（`.github/workflows/ci.yml`），在 push 或 PR 到 main 分支时自动执行：

1. **单元测试 + 覆盖率** — 运行 pytest，覆盖率不低于 90%
2. **语法编译检查** — compileall 验证所有目录
3. **代码风格** — ruff 检查（E/F/W/I/UP 规则）
4. **类型检查** — mypy 检查 common/ 和 tests/
5. **用例收集基线** — check_collect.py 验证用例数量

另有定时工作流：
- `asc_daily.yml` — iOS App Store Connect 日报
- `harmony_daily.yml` — 鸿蒙 AGC 日报
- `periodic_report.yml` — 周报/月报

## 代码质量工具

### pre-commit hooks

安装 pre-commit 后，执行以下命令启用：

```bash
pip install pre-commit
pre-commit install
```

配置了 ruff（代码风格 + 自动修复）和 mypy（类型检查）两个 hook。

### 本地运行检查

```bash
# 代码风格检查
ruff check .

# 类型检查
mypy common/ tests/ --ignore-missing-imports

# 单元测试（含覆盖率）
python -m pytest tests/ -q --cov=common --cov-report=term-missing --cov-fail-under=90
```

## 配置说明

配置文件位于 `common/config.py`，包含：
- 环境配置（dev/test/prod）
- 数据库连接配置
- Redis连接配置
- 应用信息配置

### 环境变量配置

| 变量名 | 说明 | 必填 |
|--------|------|------|
| `TOKEN_KEY` | Token 加密密钥 | 是 |
| `TOKEN_VERIFY_SALT` | Token 验证盐值 | 是 |
| `DB_DEV_HOST` | 开发环境数据库地址 | 否（默认读取 Basic.yml） |
| `DB_DEV_PASSWORD` | 开发环境数据库密码 | 否 |
| `REDIS_46_HOST` | Redis 地址 | 否 |
| `IMG_API_APP_ID` | 图片 API App ID | 否 |
| `IMG_API_APP_SECRET` | 图片 API App Secret | 否 |

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
