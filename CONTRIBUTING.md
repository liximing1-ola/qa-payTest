# 贡献指南

感谢你对 QA-PayTest 项目的关注！本文档将帮助你快速搭建开发环境并了解项目的代码规范与协作流程。

## 开发环境搭建

### 前置要求

- Python 3.11 或 3.12
- Git
- pip（随 Python 安装）

### 安装步骤

```bash
# 1. 克隆仓库
git clone <repo-url>
cd qa-payTest

# 2. 创建虚拟环境（推荐）
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 安装 pre-commit hooks
pre-commit install
```

## 代码规范

### Ruff（代码风格与静态检查）

项目使用 [Ruff](https://docs.astral.sh/ruff/) 进行代码风格检查和自动修复。

- **目标版本**：Python 3.11
- **行宽限制**：120 字符
- **启用规则**：`E`（pycodestyle errors）、`F`（pyflakes）、`W`（pycodestyle warnings）、`I`（isort）、`UP`（pyupgrade）、`B`（flake8-bugbear）、`SIM`（flake8-simplify）

```bash
# 手动运行检查
ruff check .

# 自动修复
ruff check . --fix
```

### Mypy（类型检查）

项目使用 [mypy](https://mypy-lang.org/) 进行静态类型检查，配置为 `check_untyped_defs = true`。

```bash
# 对 common 和 tests 目录进行类型检查
mypy common tests --ignore-missing-imports
```

注意事项：
- 第三方库若无类型存根，使用 `--ignore-missing-imports` 跳过
- 对 dataclass 动态添加属性（如兼容性 property）时，需添加 `# type: ignore[attr-defined]` 注释

## 测试规范

### 运行测试

```bash
# 运行所有单元测试（推荐）
python -m pytest tests/ -q

# 运行单个测试文件
python -m pytest tests/test_config.py -q

# 运行特定测试函数
python -m pytest tests/test_config.py::test_function_name -q
```

### 覆盖率

CI 在 Python 3.11 上强制覆盖率门禁 ≥ 90%：

```bash
# 本地生成覆盖率报告
python -m pytest tests/ --cov=common --cov-report=term-missing --cov-report=html --cov-fail-under=90
```

HTML 覆盖率报告将输出到 `htmlcov/` 目录，可在浏览器打开 `htmlcov/index.html` 查看。

### 测试编写要求

- 测试文件位于 `tests/` 目录，命名以 `test_` 开头
- 测试函数以 `test_` 开头
- 避免在单元测试中依赖外部网络或后端服务
- 使用 mock 隔离数据库、Redis 等外部依赖

## 提交流程

### Pre-commit Hooks

项目配置了 pre-commit hooks，在每次提交时自动运行：

- **ruff**（`v0.9.0`）：代码风格检查并自动修复
- **mypy**（`v1.14.1`）：类型检查

安装 hooks：

```bash
pre-commit install
```

手动对所有文件运行 hooks：

```bash
pre-commit run --all-files
```

### Commit Message 规范

提交信息应清晰描述变更内容，建议格式：

```
<type>: <简短描述>

[可选正文]
```

常用 type：
- `feat`：新功能
- `fix`：修复 bug
- `refactor`：重构
- `test`：测试相关
- `ci`：CI/CD 配置
- `docs`：文档
- `chore`：依赖更新、工具配置等

## CI 门禁说明

所有 PR 和 push 到 `main` 分支的提交都会触发 CI 流水线（`.github/workflows/ci.yml`），在 Python 3.11 和 3.12 上运行以下检查：

| 步骤 | 说明 | 失败影响 |
|------|------|----------|
| 单元测试 | `pytest tests/ -q`，Python 3.11 附带覆盖率 ≥ 90% 门禁 | 阻塞合并 |
| 语法编译检查 | `python -m compileall` 全目录编译验证 | 阻塞合并 |
| Ruff 检查 | `ruff check .` 代码风格 | 阻塞合并 |
| Mypy 检查 | `mypy common tests --ignore-missing-imports` 类型检查 | 阻塞合并 |
| 用例收集基线 | `python check_collect.py` 确保用例可被正常收集 | 阻塞合并 |
| 安全审计 | `pip-audit --desc` 依赖漏洞扫描 | 仅告警（continue-on-error） |

CI 全部通过后 PR 才可合并。若本地 pre-commit hooks 已安装并通过，CI 通常不会有问题。
