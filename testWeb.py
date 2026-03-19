import time
import random
import logging
from datetime import datetime
import argparse
from typing import List, Optional

# 配置日志
logging.basicConfig(
    filename='loop_printer.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


def generate_random_content() -> str:
    types = [
        lambda: f"random: {random.randint(1, 1000)}",
        lambda: f"randomString: {''.join(random.choices('abcdefghikhhdjdgwvwudhdbdklskjklmnopqrstuvwxyz', k=8))}",
        lambda: f"randomHttp: {random.choice(['OK', 'WARN', 'INFO', 'DEBUG'])}"
    ]
    return random.choice(types)()


class AdvancedLoopPrinter:
    def __init__(self):
        # 预设内容池（可动态扩展）
        self.content_pools = {
            "default": ["测试数据生成中", "检验数据中", "查询服务输出...", "接口服务状态正常"],
            "numbers": [f"数值: {i}" for i in range(100)],
            "random": []  # 动态生成随机内容
        }
        self.counter = 0  # 全局计数
        self.start_time = None  #
        self.paused = False  # 暂停状态

    def get_content(self, pool_name: str) -> str:
        if pool_name == "random":
            return generate_random_content()
        if pool_name in self.content_pools:
            # 循环取值
            return self.content_pools[pool_name][self.counter % len(self.content_pools[pool_name])]
        return f"未知内容池: {pool_name}"

    def print_with_style(self, content: str, style: str = "normal") -> None:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        base_str = f"[{timestamp}] [{self.counter:05d}] {content}"

        if style == "highlight":
            print(f"\033[1;32m{base_str}\033[0m")
        elif style == "warning":
            print(f"\033[1;33m{base_str}\033[0m")
        elif style == "error":
            print(f"\033[1;31m{base_str}\033[0m")
        else:
            print(base_str)

    def calculate_progress(self) -> Optional[str]:
        """循环计算并返回进度信息"""
        if self.total_times is None:
            return None
        progress = (self.counter / self.total_times) * 100
        bar_length = 20
        filled_length = int(bar_length * progress // 100)
        bar = '#' * filled_length + '-' * (bar_length - filled_length)
        return f"进度: [{bar}] {progress:.1f}% ({self.counter}/{self.total_times})"

    def run(self,
            pool_name: str = "default",
            total_times: Optional[int] = None,
            interval: float = 1.0,
            style: str = "normal",
            log: bool = False):
        self.total_times = total_times  # 处理逻辑
        self.start_time = datetime.now()
        self.counter = 0

        print(f"=== 接口任务执行开始 ===")
        print(f"内容池: {pool_name} | 次数: {total_times if total_times else '无限'} | 间隔: {interval}秒")
        print(f"按 'p' ，'q' ，选择任意键刷新\n")

        try:
            while True:
                if total_times is not None and self.counter >= total_times:
                    break

                if self.paused:
                    time.sleep(1)
                    continue

                content = self.get_content(pool_name)
                self.print_with_style(content, style)

                # 打印日志查看结果
                if log:
                    logging.info(f"for {self.counter}: {content}")

                progress = self.calculate_progress()
                if progress:
                    print(f"  {progress}\n")

                self.counter += 1
                time.sleep(interval)

        except KeyboardInterrupt:
            print("\nBreak，退出ING...")
        finally:
            elapsed = (datetime.now() - self.start_time).total_seconds()
            print(f"\n=== 任务结束 ===")
            print(f"执行次数: {self.counter} | hs: {elapsed:.2f}秒 | 平均每次: {elapsed / self.counter:.4f}秒")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="")
    parser.add_argument("-p", "--pool", default="default",
                        help="pool (default/numbers/random)")
    parser.add_argument("-t", "--times", type=int,
                        help="cycle")
    parser.add_argument("-i", "--interval", type=float, default=1.0,
                        help="jg（s）")
    parser.add_argument("-s", "--style", default="normal",
                        help="style (normal/highlight/warning/error)")
    parser.add_argument("-l", "--log", action="store_true",
                        help="log")  # 校验服务端脚本数据准确性
    args = parser.parse_args()

    printer = AdvancedLoopPrinter()
    printer.run(
        pool_name=args.pool,
        total_times=args.times,
        interval=args.interval,
        style=args.style,
        log=args.log
    )