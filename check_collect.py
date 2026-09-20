# coding=utf-8
"""
用例收集基线校验（离线，无需后端环境）

运行 pytest --collect-only 并核对用例总数，防止用例文件损坏、
导入错误或误删导致测试覆盖静默下降。CI 与本地通用：

    python check_collect.py
"""
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
# 全仓用例收集基线（调整用例数量时需同步更新此值）
EXPECTED_COLLECT_COUNT = 407


def main():
    proc = subprocess.run(
        [sys.executable, '-m', 'pytest', '--collect-only', '-q'],
        cwd=str(REPO_ROOT), capture_output=True, text=True)
    output = (proc.stdout or '') + (proc.stderr or '')
    match = re.search(r'(\d+)\s+tests?\s+collected', output)
    if match is None or proc.returncode != 0:
        print(output[-3000:])
        print('[FAIL] 收集过程异常（未解析到用例总数或返回码非 0）', file=sys.stderr)
        return 1
    count = int(match.group(1))
    if count != EXPECTED_COLLECT_COUNT:
        print('[FAIL] 收集数量偏离基线: 期望 %d, 实际 %d'
              % (EXPECTED_COLLECT_COUNT, count), file=sys.stderr)
        return 1
    print('[OK] collect 基线校验通过: %d 个用例' % count)
    return 0


if __name__ == '__main__':
    sys.exit(main())
