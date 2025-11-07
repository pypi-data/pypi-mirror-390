from __future__ import annotations

from textual.screen import ModalScreen
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import DataTable, Input, Button, Static, Markdown
from textual import on
from textual.message import Message

from ketacli.sdk.ai.skills.registry import SkillsRegistry
from ketacli.sdk.ai.skills.loader import load_skill_by_name


class SkillsBrowserModal(ModalScreen):
    """技能浏览器：左侧列表（元信息），右侧详情（懒加载 description）。"""

    CSS = """
    SkillsBrowserModal {
        align: center middle;
    }
    .root {
        width: 90%;
        height: 80%;
        border: round;
        padding: 1 2;
        background: $surface;
    }
    .left {
        width: 50%;
        height: 1fr;
    }
    .right {
        width: 50%;
        height: 1fr;
    }
    .toolbar {
        height: 3;
    }
    #skill-table {
        height: 1fr;
        min-height: 24;
        overflow: auto;
    }
    .desc {
        height: 1fr;
        overflow: auto;
    }
    """

    def __init__(self) -> None:
        super().__init__()
        self.registry = SkillsRegistry()
        self._metas = []
        self._filter_text = ""
        self._selected_name = None
        self._selected_names: set[str] = set()

    class SkillChosen(Message):
        def __init__(self, name: str, skill):
            super().__init__()
            self.name = name
            self.skill = skill

    class SkillsChosenMulti(Message):
        def __init__(self, names: list[str], skills: list):
            super().__init__()
            self.names = names
            self.skills = skills

    def compose(self) -> ComposeResult:
        yield Horizontal(
            Vertical(
                Static("技能列表", classes="toolbar"),
                Input(placeholder="搜索 name/summary/triggers...", id="skill-search"),
                DataTable(id="skill-table"),
                Horizontal(
                    Button("添加到选择", id="add"),
                    Button("选择并开始", id="choose"),
                    Button("重建索引", id="reload"),
                ),
                classes="left",
            ),
            Vertical(
                Static("技能详情", classes="toolbar"),
                Markdown(id="skill-desc", classes="desc"),
                Static(id="skill-meta"),
                Static("已选择：<无>", id="selected-list"),
                Button("开始任务", id="start"),
                Button("关闭", id="close"),
                classes="right",
            ),
            classes="root",
        )

    def on_mount(self) -> None:
        self._build_and_fill()

    def _build_and_fill(self) -> None:
        self.registry.build()
        self._metas = self.registry.list_metas()
        table = self.query_one("#skill-table", DataTable)
        table.clear()
        table.cursor_type = "row"
        if not table.columns:
            table.add_columns("name", "summary", "enabled", "permissions", "source_path")
        for m in self._iter_filtered_metas():
            perms = ", ".join(m.permissions or []) if isinstance(m.permissions, list) else m.permissions or ""
            table.add_row(m.name, m.summary or "", str(bool(m.enabled)), perms, m.source_path or "")
        # 冲突/错误摘要提示
        summary = self.registry.summary()
        if summary:
            self.app.notify(summary, severity="warning")

    def _update_selected_list(self) -> None:
        """刷新右侧已选择技能的展示文本"""
        try:
            txt = "已选择：" + (", ".join(sorted(self._selected_names)) if self._selected_names else "<无>")
            self.query_one("#selected-list", Static).update(txt)
        except Exception:
            pass

    def _iter_filtered_metas(self):
        text = (self._filter_text or "").strip().lower()
        if not text:
            for m in self._metas:
                yield m
            return
        for m in self._metas:
            hay = " ".join([
                m.name or "",
                m.summary or "",
                " ".join(m.triggers or []),
            ]).lower()
            if text in hay:
                yield m

    @on(Input.Changed)
    def on_search_changed(self, event: Input.Changed) -> None:
        if event.input.id != "skill-search":
            return
        self._filter_text = event.value or ""
        self._build_and_fill()

    @on(Button.Pressed)
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "reload":
            self.registry.reload()
            self._build_and_fill()
            self.app.notify("技能索引已重建", severity="success")
        elif event.button.id == "add":
            name = self._selected_name
            if not name:
                self.app.notify("请先在列表中选择一个技能", severity="warning")
                return
            self._selected_names.add(name)
            self._update_selected_list()
            self.app.notify(f"已添加到选择：{name}", severity="success")
        elif event.button.id == "choose":
            name = self._selected_name
            if not name:
                self.app.notify("请先在列表中选择一个技能", severity="warning")
                return
            try:
                skill = load_skill_by_name(name)
            except Exception as e:
                self.app.notify(f"加载技能失败: {e}", severity="error")
                return
            if not skill:
                self.app.notify(f"未找到技能: {name}", severity="warning")
                return
            self.post_message(SkillsBrowserModal.SkillChosen(name, skill))
            self.dismiss()
        elif event.button.id == "start":
            names = list(sorted(self._selected_names))
            if not names and self._selected_name:
                names = [self._selected_name]
            if not names:
                self.app.notify("请先选择至少一个技能", severity="warning")
                return
            skills = []
            try:
                for n in names:
                    s = load_skill_by_name(n)
                    if s:
                        skills.append(s)
                if not skills:
                    self.app.notify("未能加载任何技能", severity="error")
                    return
                self.post_message(SkillsBrowserModal.SkillsChosenMulti(names, skills))
                self.dismiss()
            except Exception as e:
                self.app.notify(f"加载技能失败: {e}", severity="error")
        elif event.button.id == "close":
            self.dismiss()

    @on(DataTable.RowSelected)
    def on_row_selected(self, event: DataTable.RowSelected) -> None:
        table = self.query_one("#skill-table", DataTable)
        row = table.get_row(event.row_key)
        if not row:
            return
        name = row[0]
        self._selected_name = name
        # 懒加载描述
        try:
            skill = load_skill_by_name(name)
        except Exception as e:
            self.app.notify(f"加载技能失败: {e}", severity="error")
            return
        if not skill:
            self.app.notify(f"未找到技能: {name}", severity="warning")
            return
        desc = skill.description or "(无描述)"
        self.query_one("#skill-desc", Markdown).update(desc)
        # 显示附加元信息
        meta_lines = []
        meta = skill.meta
        meta_lines.append(f"permissions: {', '.join(meta.permissions or []) if meta.permissions else '(未设置)'}")
        meta_lines.append(f"tools_whitelist: {', '.join(meta.tools_whitelist or []) if meta.tools_whitelist else '(未设置)'}")
        self.query_one("#skill-meta", Static).update("\n".join(meta_lines))
        # 更新已选列表显示（不自动添加，仅刷新展示）
        self._update_selected_list()