# coding=utf-8
"""
用例收集基线校验（离线，无需后端环境）

运行 pytest --collect-only 并核对用例总数，防止用例文件损坏、
导入错误或误删导致测试覆盖静默下降。CI 与本地通用：

    python check_collect.py

CI 兼容性设计（GitHub windows-latest runner 为英文区域，捕获管道
默认 cp1252 码页，中文 print / 区域码页解码均会触发 Unicode 错误）：
- 状态消息一律使用英文，从源头规避窄码页编码失败；
- stdout/stderr 显式 reconfigure(errors="replace")，写入异常时替换而非抛错；
- subprocess 显式 encoding="utf-8", errors="replace"，与子进程区域码页解耦；
- 失败时输出 ::error:: 工作流命令生成 annotation（匿名 API 可读取），
  并追加写入 GITHUB_STEP_SUMMARY，便于在无日志权限时定位失败原因。
"""
import os
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
# 全仓用例收集基线（调整用例数量时需同步更新此值）
EXPECTED_COLLECT_COUNT = 511


def _configure_stdio():
    """stdout/stderr 遇不可编码字符时替换而非抛错（兼容 cp1252 等窄码页管道）。"""
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, 'reconfigure', None)
        if reconfigure is not None:
            try:
                reconfigure(errors='replace')
            except (ValueError, OSError):
                pass


def _collapse(text):
    """压缩空白为单行摘要，避免换行/控制字符破坏 ::error:: 注解格式。"""
    return ' '.join(text.split())[:500]


def _report_failure(message):
    """经 GitHub annotation（::error::）与 job summary 双通道报告失败原因。"""
    print('::error::check_collect: %s' % _collapse(message))
    summary_path = os.environ.get('GITHUB_STEP_SUMMARY')
    if summary_path:
        try:
            with open(summary_path, 'a', encoding='utf-8') as fh:
                fh.write('#### check_collect failed\n\n```text\n%s\n```\n' % message)
        except OSError:
            pass


def main():
    _configure_stdio()
    proc = subprocess.run(
        [sys.executable, '-m', 'pytest', '--collect-only', '-q'],
        cwd=str(REPO_ROOT), capture_output=True,
        encoding='utf-8', errors='replace')
    output = (proc.stdout or '') + (proc.stderr or '')
    match = re.search(r'(\d+)\s+tests?\s+collected', output)
    if match is None or proc.returncode != 0:
        tail = output[-3000:]
        print(tail)
        _report_failure(
            'collect aborted: pytest exit=%s, count not parsed. tail: %s'
            % (proc.returncode, tail))
        return 1
    count = int(match.group(1))
    if count != EXPECTED_COLLECT_COUNT:
        _report_failure('collect count mismatch: expected %d, actual %d'
                        % (EXPECTED_COLLECT_COUNT, count))
        return 1
    print('[OK] collect baseline check passed: %d cases' % count)
    return 0


if __name__ == '__main__':
    sys.exit(main())
