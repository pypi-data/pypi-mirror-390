from __future__ import annotations

from enum import Enum
from typing import List
import time

from triclick_doc_toolset.framework.context import Context
from triclick_doc_toolset.framework.command import Command


class ExecMode(Enum):
    """策略执行模式枚举，约束为三种：顺序、并行、条件。"""
    SEQUENTIAL = "sequential"  # 顺序执行
    PARALLEL = "parallel"      # 并行执行（当前实现按顺序运行，预留并行语义）


class Strategy:
    """策略（Strategy）用于组织一组命令并控制其执行方式。

    参数：
    - name: 策略名，便于定位与日志输出。
    - priority: 策略优先级，数值越小越先执行。
    - commands: 命令列表，按策略定义的方式执行。
    - exec_mode: 执行模式，使用 ExecMode 枚举。
    """

    def __init__(
        self,
        name: str,
        priority: int,
        commands: List[Command],
        exec_mode: ExecMode = ExecMode.SEQUENTIAL,
    ):
        self.name = name
        self.priority = priority
        # 优先级语义调整：命令按优先级升序（小值先执行）
        self.commands = sorted(commands, key=lambda c: c.priority)
        self.exec_mode = exec_mode

    def apply(self, context: Context) -> Context:
        """按照策略执行方式应用命令列表到上下文。"""
        if self.exec_mode == ExecMode.SEQUENTIAL:
            return self._execute_sequential(context)
        elif self.exec_mode == ExecMode.PARALLEL:
            # TODO 当前实现：串行运行，预留并行接口以保持语义一致
            return self._execute_sequential(context)
        else:
            raise ValueError(f"Unsupported execution mode: {self.exec_mode}")

    def _execute_sequential(self, context: Context) -> Context:
        ctx = context
        for cmd in self.commands:
            try:
                if not cmd.check_condition(ctx):
                    ctx.errors.append(f"Command {cmd.name} skipped: condition not met")
                    continue
                if not cmd.is_satisfied(ctx):
                    ctx.errors.append(f"Command {cmd.name} skipped: is_satisfied returned False")
                    continue
                start = time.perf_counter()
                ctx = cmd.execute(ctx)
                elapsed = time.perf_counter() - start
                print(f"[{cmd.name}] 耗时 {elapsed:.2f}s")
            except Exception as e:
                ctx.errors.append(f"Command {cmd.name} failed: {e}")
        return ctx