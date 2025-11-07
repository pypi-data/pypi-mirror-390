"""任务管理器Widget

在TUI界面展示当前任务的各步骤及状态。
使用Textual的DataTable组件，避免自定义复杂实现。
"""

from typing import List, Dict, Optional

from textual.app import ComposeResult
from textual.containers import Container, Vertical
from textual.widgets import Label, DataTable
from rich.text import Text as RichText


class TaskManagerWidget(Container):
    """任务管理器主组件

    - 展示步骤列表：序号、标题、状态、迭代次数
    - 提供更新状态的API供逻辑层调用
    """

    DEFAULT_CSS = """
    TaskManagerWidget {
        height: 100%;
    }
    #task-header {
        dock: top;
        height: 3;
        background: $surface;
        color: $text;
    }
    #task-table {
        height: 1fr;
        border: solid $secondary;
    }
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._table: Optional[DataTable] = None
        # 内部数据：index -> {title, status, iteration}
        self._rows: Dict[int, Dict] = {}

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Label("📋 任务状态", id="task-header")
            table = DataTable(id="task-table")
            # 列：步骤、标题、状态、迭代
            table.add_columns("步骤", "标题", "状态", "迭代")
            self._table = table
            yield table

    # 公共API
    def set_tasks(self, steps: List[str]) -> None:
        """设置任务步骤列表，默认状态为 pending"""
        if not self._table:
            return
        self._table.clear()
        self._rows.clear()
        for i, s in enumerate(steps, start=1):
            title = (s or "").strip()
            row = {
                "title": title,
                "status": "pending",
                "iteration": 0,
            }
            self._rows[i] = row
            cells = self._styled_row_cells(i, title, row["status"], row["iteration"])
            self._table.add_row(*cells)

        # 当设置了任务步骤且非空时，自动打开右侧任务侧栏
        try:
            sidebar = self.app.query_one("#task-sidebar")
            if steps:
                # 有任务：显示侧栏
                if "hidden" in sidebar.classes:
                    sidebar.remove_class("hidden")
            else:
                # 无任务：隐藏侧栏
                if "hidden" not in sidebar.classes:
                    sidebar.add_class("hidden")
        except Exception:
            pass

    def update_status(self, index: int, status: str, iteration: Optional[int] = None) -> None:
        """更新某一步的状态与迭代次数"""
        if not self._table:
            return
        if index not in self._rows:
            return
        row = self._rows[index]
        row["status"] = status
        if iteration is not None:
            row["iteration"] = iteration
        # 更新整行样式与内容：行序号为 index-1
        try:
            styled_cells = self._styled_row_cells(index, row["title"], row["status"], row["iteration"])
            # 逐单元更新，确保整行背景一致
            for col, cell in enumerate(styled_cells):
                self._table.update_cell(index - 1, col, cell)
        except Exception:
            # 兼容不同版本的DataTable，若update_cell不可用则重绘整表
            self._redraw_table()

        # 任意状态更新时确保侧栏可见
        try:
            sidebar = self.app.query_one("#task-sidebar")
            if "hidden" in sidebar.classes:
                sidebar.remove_class("hidden")
        except Exception:
            pass

    def _redraw_table(self):
        if not self._table:
            return
        self._table.clear()
        for i in sorted(self._rows.keys()):
            row = self._rows[i]
            cells = self._styled_row_cells(i, row["title"], row["status"], row["iteration"]) 
            self._table.add_row(*cells)

    def _fmt_status(self, status: str) -> str:
        """状态文本（去除颜色标记，仅保留emoji）"""
        mapping = {
            "pending": "待执行 ⏳",
            "in_progress": "执行中 🔧",
            "completed": "已完成 ✅",
            "paused": "已暂停 ⏸️",
            "blocked": "被阻塞 🛑",
        }
        return mapping.get(status, status)

    def _fg_style_for_status(self, status: str) -> str:
        """根据状态返回整行文字颜色样式"""
        # 文字颜色：
        # - completed: 绿色
        # - in_progress: 黄色
        # - pending: 白色
        # 其他状态：合理颜色以便区分
        if status == "completed":
            return "green"
        if status == "in_progress":
            return "yellow"
        if status == "pending":
            return "white"
        if status == "blocked":
            return "red"
        if status == "paused":
            return "red"
        return ""

    def _styled_row_cells(self, i: int, title: str, status: str, iteration: int):
        """构造整行带文字颜色样式的 RichText 单元格"""
        fg = self._fg_style_for_status(status)
        # 每个单元格使用相同前景色，形成整行统一文字颜色
        step_cell = RichText(str(i), style=fg)
        title_cell = RichText(title, style=fg)
        status_cell = RichText(self._fmt_status(status), style=fg)
        iter_cell = RichText(str(iteration), style=fg)
        return (step_cell, title_cell, status_cell, iter_cell)