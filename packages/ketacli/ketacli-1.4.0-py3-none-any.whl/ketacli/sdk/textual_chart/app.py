"""主应用类"""

import asyncio
from datetime import datetime
import os
import logging
from textual.app import App, ComposeResult
from textual.containers import Container, Vertical, Horizontal
from textual.widgets import Header, Footer, Static, Button
from textual.worker import Worker
from textual import on

from .data_models import ChatSession, SessionManager
from .widgets import (
    ModelSelectorWidget, ChatHistoryWidget, ChatInputWidget, 
    CustomTextArea, ToolsListModal, SessionHistoryModal, ContextWindowModal,
    ModelConfigManagerWidget, TaskManagerWidget
)
from .widgets.skills_browser import SkillsBrowserModal
from ketacli.sdk.ai.skills.models import Skill
from ketacli.sdk.ai.skills.registry import SkillsRegistry
from ketacli.sdk.ai.skills.selector import select_best_skill, select_skills_by_model_sync
from ketacli.sdk.ai.skills.loader import load_skill_by_name
from .widgets.config_widgets import ModelConfigModal
from .styles import CSS
from .context_manager import ContextManager, SessionContextManager
from .token_calculator import calculate_token_stats
from .utils.ai_helpers import (
    plan_task_steps_v2,
    get_enabled_tools_openai_format,
)
from .utils.chat_flow import process_ai_response
from .utils.chat_stream import augment_system_prompt, sanitize_tool_messages, enforce_openai_tool_sequence, process_tool_sequence
from ketacli.sdk.ai.client import AIClient

# 轻量日志：写入到仓库根目录的 log/textual_debug.log
logger = logging.getLogger("ketacli.textual")
if not logger.handlers:
    logger.setLevel(logging.DEBUG)
    try:
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
        log_dir = os.path.join(base_dir, "log")
        os.makedirs(log_dir, exist_ok=True)
        # 初始化时清空日志文件
        log_path = os.path.join(log_dir, "textual_debug.log")
        with open(log_path, "w", encoding="utf-8"):
            pass
        fh = logging.FileHandler(log_path)
        fh.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
        logger.addHandler(fh)
    except Exception:
        # 若文件日志初始化失败，不影响运行
        pass


class InteractiveChatApp(App):
    """交互式聊天应用"""
    
    CSS = CSS
    
    BINDINGS = [
        ("q", "quit", "退出"),
        ("c", "clear_chat", "清空对话"),
        ("n", "clear_chat", "新会话"),
        ("t", "show_tools", "显示工具"),
        ("i", "focus_input", "聚焦输入框"),
        ("h", "show_session_history", "历史会话"),
        ("m", "show_model_config", "模型配置"),
        ("k", "show_context", "上下文"),
        ("s", "show_skills", "技能浏览"),
        ("r", "toggle_task_sidebar", "打开/关闭任务栏"),
    ]
    
    def __init__(self, **kwargs):
        """初始化交互式聊天应用
        
        初始化应用状态，包括AI客户端、会话管理、上下文管理和工具配置等
        
        Args:
            **kwargs: 传递给父类App的参数
        """
        super().__init__(**kwargs)
        self.ai_client = AIClient()
        self.conversation_history = []
        self.user_raw_inputs = [] # 存储用户原始输入
        self._chat_in_progress = False
        self._current_ai_task = None  # 当前AI响应任务
        # 规划状态锁：一次会话仅允许一次任务规划
        self.plan_execution_in_progress = False
        self.planning_locked = False
        
        # 是否启用流式输出（可通过模型配置或外部参数覆盖）
        self.enable_streaming = True
        
        # 上下文管理器
        self.context_manager = ContextManager()
        self.session_context_manager = SessionContextManager()
        self.session_manager = SessionManager()
        self.current_session = None
        self.current_skill: Skill | None = None
        # 多技能支持：当前已选技能列表（保留 current_skill 兼容单技能逻辑）
        self.current_skills: list[Skill] = []
        # 技能注册表与自动选择开关
        self.skills_registry = SkillsRegistry()
        self._skills_loaded = False
        self.auto_skill_enabled = True

        # 工具启用状态：默认开启资源列出、日志/指标搜索、获取文档
        # 对应函数名：list_assets, list_queryable_assets, search_data_for_log, search_data_for_metric, get_docs
        self.enabled_tools = {
            "list_assets",
            "list_queryable",
            "search_data",
            "get_repo_fields",
            "get_docs",
        }
        
        # 通知过滤配置：仅展示重要信息（error/warning/success）
        self._important_severities = {"error", "warning", "success"}
        # 明显的调试/噪音标记，统一屏蔽
        self._debug_markers = ("DEBUG", "🧪", "🔧", "➡️", "🔗", "⚙️", "📩", "🛠️", "🧹", "🔁")

    def notify(self, message, **kwargs):
        """统一过滤通知（委托公共过滤逻辑），仅保留重要提示。"""
        try:
            from .utils import filter_notification
        except Exception:
            # 回退：若导入失败，仍直接调用父类
            if "markup" not in kwargs:
                kwargs['markup'] = False
            return super().notify(message, **kwargs)
        should_send, prepared = filter_notification(message, kwargs, getattr(self, "_debug_markers", ()))
        if not should_send:
            return
        return super().notify(message, **prepared)
        
    def compose(self) -> ComposeResult:
        """构建应用UI布局
        
        定义应用的界面结构，包括头部、聊天容器和底部组件
        
        Returns:
            ComposeResult: 包含UI组件的生成器结果
        """
        yield Header()
        
        with Container(classes="chat-container"):
            yield Static("🤖 AI智能对话助手", classes="chat-header")

            # 左右分栏布局：左侧为聊天区域，右侧为任务管理器
            with Horizontal(classes="chat-body"):
                with Vertical(classes="chat-left"):
                    yield ModelSelectorWidget(id="model-selector")
                    yield ChatHistoryWidget(id="chat-history", classes="chat-history")
                    yield ChatInputWidget(id="chat-input", classes="chat-input-container")
                with Vertical(id="task-sidebar", classes="chat-right hidden"):
                    yield TaskManagerWidget(id="task-manager")
                
        yield Footer()
        
    def on_mount(self) -> None:
        """应用挂载时的初始化操作
        
        在应用UI完成挂载后执行初始化操作，包括初始化AI客户端和添加欢迎消息
        """
        self._initialize_ai_client()
        self._add_welcome_message()
        
    def _initialize_ai_client(self):
        """初始化AI客户端
        
        从系统提示词文件加载提示词并创建AI客户端实例。
        如果初始化失败，会显示错误通知。
        """
        try:
            # 修正系统提示词文件路径，指向 sdk/ai/prompts/system.md
            prompt_path = os.path.abspath(
                os.path.join(os.path.dirname(__file__), "../ai/prompts/system.md")
            )
            with open(prompt_path, "r", encoding="utf-8") as f:
                system_prompt = f.read()
            self.ai_client = AIClient(system_prompt=system_prompt)
            # 读取模型配置中的 streaming 开关（若存在）
            try:
                # 1) 直接字段
                self.enable_streaming = bool(getattr(self.ai_client.model_config, "streaming", self.enable_streaming))
                # 2) extra_params 中的 streaming / enable_streaming / stream
                extra = getattr(self.ai_client.model_config, "extra_params", {}) or {}
                for key in ("streaming", "enable_streaming", "stream"):
                    if key in extra:
                        self.enable_streaming = bool(extra.get(key))
                        break
            except Exception:
                pass
        except Exception as e:
            self.notify(f"AI客户端初始化失败: {e}", severity="error")
            
    def _add_welcome_message(self):
        """添加欢迎消息
        
        在聊天历史中添加欢迎消息，包括功能介绍、示例和当前启用的工具列表。
        """
        chat_history = self.query_one("#chat-history", ChatHistoryWidget)
        welcome_msg = f"""👋 欢迎使用 KetaOps AI 交互助手！

我可以帮助你：
- 📊 数据查询与分析（日志/指标/资产）
- 🔍 智能搜索与问题定位（关键字、TraceID、主机）
- 📈 指标趋势与可视化（折线/柱状/单值）
- 🛠️ 资源管理与诊断（仓库/权限/配置）

推荐示例（具体任务）：
- 从`logs_keta`提取`level=WARN`且包含“forbidden”的记录
- 统计主机内存使用趋势（最近24h）
- 统计最近3天主机CPU利用率（按`host`分组）
- 创建一个测试仓库并向里面写入100条测试数据
- 执行命令：`ketacli config list-clusters`

快捷键提示：`i` 聚焦输入、`h` 历史会话、`t` 工具开关、`m` 模型配置、`k` 上下文、`s` 技能浏览、`r` 切换任务侧栏、`q` 退出。"""
        
        chat_history.add_message("assistant", welcome_msg)

    def _get_enabled_tools_openai_format(self):
        """获取已启用工具的OpenAI格式定义列表
        
        从全局工具注册表中筛选出已启用的工具，并返回其OpenAI格式定义。
        
        Returns:
            list: 已启用工具的OpenAI格式定义列表，如果出错则返回空列表
        """
        return get_enabled_tools_openai_format(self.enabled_tools)
        
    def on_chat_input_widget_stop_requested(self, message: ChatInputWidget.StopRequested) -> None:
        """处理聊天输入控件的停止请求事件
        
        当用户请求停止当前AI任务时触发，取消正在进行的AI任务并重置相关状态。
        
        Args:
            message: 停止请求事件对象
        """
        """处理停止请求"""
        if self._current_ai_task:
            self._current_ai_task.cancel()
            self._current_ai_task = None
            self._chat_in_progress = False
            # 保持计划暂停状态与锁，防止后续消息触发重新规划
            try:
                setattr(self, "plan_status", "paused")
                setattr(self, "plan_execution_in_progress", True)
                setattr(self, "planning_locked", True)
                logger.debug("[stop] 手动停止：标记计划为 paused，锁定规划=True，执行中=True")
            except Exception:
                pass
            
            # 重置按钮状态
            chat_input = self.query_one("#chat-input", ChatInputWidget)
            chat_input.set_processing(False)
            
            # 显示停止消息
            chat_history = self.query_one("#chat-history", ChatHistoryWidget)
            if chat_history._current_streaming_widget:
                chat_history.finish_streaming_message("**[已停止响应]**")
            else:
                try:
                    # 非流式模式下也给出停止提示
                    chat_history.add_message("assistant", "**[已停止响应]**")
                except Exception:
                    pass
            
            self.notify("已停止AI响应", severity="success")

    def on_chat_input_widget_message_sent(self, message: ChatInputWidget.MessageSent) -> None:
        """处理聊天输入控件的消息发送事件
        
        当用户在聊天输入控件中发送消息时触发，将用户消息添加到聊天历史并启动AI响应处理。
        
        Args:
            message: 消息发送事件对象
        """
        # 调试：记录收到的用户消息
        try:
            msg_preview = (message.message or "").strip().replace("\n", " ")[:120]
            logger.debug(f"[input] 收到用户消息，长度={len(message.message or '')}，预览='{msg_preview}'，进行中={self._chat_in_progress}")
        except Exception:
            pass
        """处理用户发送的消息"""
        if self._chat_in_progress:
            chat_input = self.query_one("#chat-input", ChatInputWidget)
            chat_input.set_loading(False)
            # 进度提示弱化，减少噪音
            self.notify("对话正在进行中，请稍候...", severity="info")
            return
            
        user_message = message.message
        # 记录用户原始输入
        try:
            self.user_raw_inputs.append(user_message)
        except Exception:
            pass
        chat_history = self.query_one("#chat-history", ChatHistoryWidget)

        # 自动技能选择：在首次消息或尚未选择技能时尝试（优先模型判定，失败回退触发词）
        try:
            if self.auto_skill_enabled and (self.current_skill is None) and (not self.current_skills):
                if not self._skills_loaded:
                    self.skills_registry.reload()
                    self._skills_loaded = True
                metas = self.skills_registry.list_metas()
                # 1) 首选模型选择（同步）
                try:
                    sel = select_skills_by_model_sync(self.ai_client, user_message, metas or [])
                except Exception:
                    sel = {"mode": "none", "selected": [], "reason": "调用失败"}
                selected_names = sel.get("selected") or []
                if selected_names:
                    chosen_skills = []
                    for nm in selected_names:
                        try:
                            sk = load_skill_by_name(nm)
                            if sk:
                                chosen_skills.append(sk)
                        except Exception:
                            pass
                    if chosen_skills:
                        # 兼容单技能与多技能
                        self.current_skills = chosen_skills
                        self.current_skill = chosen_skills[0]
                        # 合并白名单（取并集）
                        wl = set()
                        for sk in chosen_skills:
                            try:
                                wl.update(set(sk.meta.tools_whitelist or []))
                            except Exception:
                                pass
                        if wl:
                            self.enabled_tools = wl
                        # UI提示
                        if len(chosen_skills) == 1:
                            meta = chosen_skills[0].meta
                            chat_history.add_message("assistant", f"🤖 已自动选择技能（模型）：{meta.name}\n摘要：{meta.summary or ''}")
                            self.notify(f"自动选择技能（模型）：{meta.name}", severity="success")
                        else:
                            names = ", ".join([getattr(sk.meta, "name", "?") for sk in chosen_skills])
                            chat_history.add_message("assistant", f"🤖 已自动选择多个技能（模型）：{names}")
                            self.notify(f"自动选择多个技能（模型）：{names}", severity="success")
                else:
                    # 2) 回退触发词选择
                    meta = select_best_skill(user_message, metas or [])
                    if meta:
                        try:
                            skill = load_skill_by_name(meta.name)
                            self.current_skill = skill
                            self.current_skills = [skill]
                            if meta.tools_whitelist:
                                self.enabled_tools = set(meta.tools_whitelist)
                            chat_history.add_message(
                                "assistant",
                                f"🤖 已自动选择技能（回退）：{meta.name}\n摘要：{meta.summary or ''}"
                            )
                            self.notify(f"自动选择技能（回退）：{meta.name}", severity="success")
                        except Exception as e:
                            self.notify(f"自动选择技能失败: {e}", severity="warning")
        except Exception:
            pass
        
        # 如果是新会话，创建会话
        if not self.current_session:
            self.current_session = ChatSession.create_new()
        
        # 添加用户消息到历史，计算token统计
        model_selector = self.query_one("#model-selector", ModelSelectorWidget)
        selected_model = model_selector.get_selected_model() or "gpt-3.5-turbo"
        
        # 计算用户消息的token统计
        user_msg_dict = {"role": "user", "content": user_message}
        context_messages = [{"role": msg["role"], "content": msg["content"]} for msg in self.conversation_history]
        user_token_stats = calculate_token_stats(
            current_message=user_msg_dict,
            context_messages=context_messages
        )
        
        chat_history.add_message("user", user_message, token_stats=user_token_stats)
        
        # 调试：记录token统计
        try:
            user_tokens = user_token_stats.get("current_tokens") if isinstance(user_token_stats, dict) else None
            ctx_tokens = user_token_stats.get("context_tokens") if isinstance(user_token_stats, dict) else None
            logger.debug(f"[input] token统计：当前={user_tokens}，上下文={ctx_tokens}，历史条数={len(self.conversation_history)}")
        except Exception:
            pass
        
        # 设置处理状态
        chat_input = self.query_one("#chat-input", ChatInputWidget)
        chat_input.set_processing(True)
        logger.debug("[flow] 启动AI响应处理任务（worker）")
        
        # 异步处理AI响应
        self._current_ai_task = self.run_worker(self._process_ai_response(user_message))
        
    

    async def _plan_task_steps(self, user_text: str) -> dict:
        """使用AI判断类型与复杂度，并返回规划结果字典。
        
        根据用户输入，AI先判断类型（问题/任务）；当为任务时按复杂度拆分为可执行步骤；问题类型不拆分，由上游直接回答。
        
        Args:
            user_text: 用户输入的文本
            
        Returns:
            dict: {"type": "question|task", "complexity": "low|high", "steps": [str]}
        """
        return await plan_task_steps_v2(
            self.ai_client,
            user_text,
            enabled_tools=self.enabled_tools,
            conversation_history=self.conversation_history,
            user_raw_inputs=getattr(self, "user_raw_inputs", []),
            skills_context=self._collect_skills_context_for_planning(),
        )
    
    async def _process_ai_response(self, user_message: str):
        """处理AI响应，委托到通用流程"""
        logger.debug(f"[flow] 进入 _process_ai_response，消息长度={len(user_message or '')}")
        await process_ai_response(self, user_message)
            
    def _augment_system_prompt(self, base: str) -> str:
        # 在通用系统提示词基础上，注入当前选择的技能摘要与详情，作为系统级指导上下文
        prompt = augment_system_prompt(base)
        try:
            skills_ctx = self._collect_skills_context_for_planning() or []
            if skills_ctx:
                blocks = []
                count = 0
                for s in skills_ctx:
                    if count >= 3:
                        break
                    name = (s or {}).get("name") or ""
                    summary = (s or {}).get("summary") or ""
                    perms = ", ".join((s or {}).get("permissions") or [])
                    tools = ", ".join((s or {}).get("tools_whitelist") or [])
                    desc = (s or {}).get("description") or ""
                    # 限制描述长度，避免过长提示污染
                    if isinstance(desc, str) and len(desc) > 1200:
                        desc = desc[:1200] + "..."
                    block = (
                        f"技能名称: {name}\n"
                        f"技能摘要: {summary}\n"
                        f"权限: {perms or '无'}\n"
                        f"工具白名单: {tools or '无'}\n"
                        f"技能说明: {desc or '无'}"
                    )
                    blocks.append(block)
                    count += 1
                guide = (
                    "[技能上下文（系统指导）]\n"
                    "以下技能是当前会话可参考的能力说明，请在需要时优先遵循其指导与可用工具：\n"
                    + "\n\n".join(blocks)
                )
                # 幂等：若已存在技能上下文标识，则不再重复追加
                if "[技能上下文（系统指导）]" not in prompt:
                    prompt = f"{prompt}\n\n{guide}".strip()
        except Exception:
            pass
        logger.debug(f"[flow] 系统提示词: {prompt}")
        logger.debug(f"[flow] 系统提示词长度={len(prompt or '')}")
        return prompt

    def _collect_skills_context_for_planning(self) -> list:
        """收集技能上下文用于步骤规划。

        返回结构化的列表，每项包含：name, summary, permissions, tools_whitelist, description。
        """
        ctx = []
        try:
            skills = list(self.current_skills or [])
            if not skills and getattr(self, "current_skill", None):
                skills = [self.current_skill]
            for s in skills:
                try:
                    m = getattr(s, "meta", None)
                    if not m:
                        continue
                    ctx.append({
                        "name": m.name,
                        "summary": m.summary or "",
                        "permissions": list(m.permissions or []) if m.permissions else [],
                        "tools_whitelist": list(m.tools_whitelist or []) if m.tools_whitelist else [],
                        "description": s.description or "",
                    })
                except Exception:
                    continue
        except Exception:
            pass
        return ctx

    def _sanitize_tool_messages(self, messages: list, provider: str) -> list:
        return sanitize_tool_messages(messages, provider)

    def _enforce_openai_tool_sequence(self, msgs: list) -> tuple[list, int, int]:
        return enforce_openai_tool_sequence(msgs)


    def _prepare_messages(self, user_message: str) -> list:
        logger.debug(f"[context] 准备消息：历史条数={len(self.conversation_history)}，用户文本长度={len(user_message or '')}")
        current_message = {"role": "user", "content": user_message}
        if len(self.conversation_history) > 20:
            self.context_manager.update_config(max_messages=15)
            original_messages = self.conversation_history
            compressed_messages = self.context_manager.process_messages(
                original_messages, force_compress=True
            )
            provider = getattr(self.ai_client.model_config, "provider", "")
            sanitized_messages = self._sanitize_tool_messages(compressed_messages, provider)
            logger.debug(f"[context] 上下文压缩：原始={len(original_messages)}，压缩后={len(compressed_messages)}，提供方={provider}")
            if len(compressed_messages) < len(original_messages):
                try:
                    stats = self.context_manager.compressor.get_compression_stats(
                        original_messages, compressed_messages
                    )
                    tokens_saved = max(
                        0,
                        stats.get("estimated_original_tokens", 0)
                        - stats.get("estimated_compressed_tokens", 0)
                    )
                    self.notify(
                        f"🗜️ 上下文已压缩: {len(original_messages)}→{len(compressed_messages)}条消息, 节省{tokens_saved}个token",
                        timeout=3
                    )
                except Exception:
                    pass
            removed_count = len(compressed_messages) - len(sanitized_messages)
            if removed_count > 0:
                logger.debug(f"[context] 工具消息规范化：移除不合规工具消息 {removed_count} 条")
                self.notify(f"已移除 {removed_count} 条不合规的工具消息，避免请求错误", severity="warning")
            logger.debug(f"[context] 返回消息数={len(sanitized_messages) + 1}")
            return sanitized_messages + [current_message]
        else:
            logger.debug(f"[context] 返回消息数={len(self.conversation_history) + 1}")
            return self.conversation_history + [current_message]

    async def _process_tool_sequence(self, messages: list) -> tuple:
        """处理工具调用序列（委托到公共实现）"""
        return await process_tool_sequence(self, messages)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """处理按钮点击事件"""
        if event.button.id == "tools-button":
            # 保持与快捷键 Ctrl+T 一致：传入当前已启用工具以预选复选框
            try:
                self.push_screen(ToolsListModal(enabled_tools=self.enabled_tools))
            except Exception:
                # 回退：若异常则仍尝试打开，但不预选
                self.push_screen(ToolsListModal())
        elif event.button.id == "new-session-button":
            self.action_clear_chat()
            
    def action_clear_chat(self) -> None:
        """清空对话历史"""
        # 保存当前会话
        self._save_current_session()
        
        # 清空对话
        chat_history = self.query_one("#chat-history", ChatHistoryWidget)
        chat_history.clear_history()
        self.conversation_history.clear()
        try:
            self.user_raw_inputs.clear()
        except Exception:
            pass
        self.current_session = None
        self._chat_in_progress = False
        # 重置技能选择状态，确保新会话可触发自动选择
        try:
            self.current_skill = None
            self.current_skills = []
            # 恢复默认启用工具集合（避免前一会话的白名单残留）
            self.enabled_tools = {
                "list_assets",
                "list_queryable",
                "search_data",
                "get_repo_fields",
                "get_docs",
            }
        except Exception:
            pass
        # 重置规划执行状态，避免残留锁影响后续会话
        self.plan_execution_in_progress = False
        self.planning_locked = False
        self._add_welcome_message()
        self.notify("对话历史已清空", severity="success")
        
    def action_show_tools(self) -> None:
        """显示工具列表"""
        try:
            self.push_screen(ToolsListModal(enabled_tools=self.enabled_tools))
        except Exception as e:
            self.notify(f"打开工具列表失败: {e}", severity="error")

    @on(ToolsListModal.ToolsSaved)
    def on_tools_list_modal_tools_saved(self, message: ToolsListModal.ToolsSaved) -> None:
        """处理工具选择保存事件"""
        try:
            selected = set(message.selected_tools or [])
            self.enabled_tools = selected
            # 简单提示当前启用工具
            names_preview = ", ".join(list(selected)[:6]) if selected else "(无)"
            self.notify(f"✅ 已更新启用工具：{names_preview}", timeout=4, severity="success")
        except Exception as e:
            self.notify(f"更新启用工具失败: {e}", severity="error")
        
    def action_show_session_history(self) -> None:
        """显示历史会话"""
        modal = SessionHistoryModal(self.session_manager)
        self.push_screen(modal)
        
    def action_show_model_config(self) -> None:
        """显示模型配置管理"""
        from .model_config_app import ModelConfigScreen
        self.push_screen(ModelConfigScreen())

    def action_toggle_task_sidebar(self) -> None:
        """切换右侧任务侧栏的显示/隐藏"""
        try:
            sidebar = self.query_one("#task-sidebar")
        except Exception:
            sidebar = None
        if not sidebar:
            try:
                self.notify("未找到任务侧栏", severity="warning")
            except Exception:
                pass
            return
        try:
            if "hidden" in sidebar.classes:
                sidebar.remove_class("hidden")
                if hasattr(self, "notify"):
                    self.notify("任务侧栏已显示", severity="information")
            else:
                sidebar.add_class("hidden")
                if hasattr(self, "notify"):
                    self.notify("任务侧栏已隐藏", severity="information")
        except Exception:
            try:
                self.notify("切换任务侧栏失败", severity="error")
            except Exception:
                pass
    
    def action_show_context(self) -> None:
        """显示上下文窗口"""
        try:
            self.push_screen(ContextWindowModal())
        except Exception as e:
            self.notify(f"打开上下文窗口失败: {e}", severity="error")

    def action_show_skills(self) -> None:
        """显示技能浏览器（列表/详情，懒加载描述）"""
        try:
            self.push_screen(SkillsBrowserModal())
        except Exception as e:
            self.notify(f"打开技能浏览器失败: {e}", severity="error")

    @on(SkillsBrowserModal.SkillChosen)
    def on_skill_chosen(self, message: SkillsBrowserModal.SkillChosen) -> None:
        """接收技能选择事件，更新当前技能并注入上下文。"""
        try:
            self.current_skill = message.skill
            # 单选时同步 current_skills（作为首个技能），兼容后续多技能逻辑
            self.current_skills = [message.skill] if message.skill else []
            meta = self.current_skill.meta
            # 若存在白名单，则将启用工具集合收敛为白名单（阶段8再严格约束）
            if meta.tools_whitelist:
                self.enabled_tools = set(meta.tools_whitelist)
            # 在对话历史中加入一个系统提示（可被压缩），提示当前技能选择
            chosen_tip = (
                f"已选择技能：{meta.name}\n"
                f"摘要：{meta.summary or ''}\n"
                f"权限：{', '.join(meta.permissions or []) if meta.permissions else '(未设置)'}\n"
                f"白名单工具：{', '.join(meta.tools_whitelist or []) if meta.tools_whitelist else '(未设置)'}"
            )
            chat_history = self.query_one("#chat-history", ChatHistoryWidget)
            chat_history.add_message("assistant", chosen_tip)
            self.notify(f"已选择技能：{meta.name}", severity="success")
        except Exception as e:
            self.notify(f"处理技能选择失败: {e}", severity="error")

    @on(SkillsBrowserModal.SkillsChosenMulti)
    def on_skills_chosen_multi(self, message: SkillsBrowserModal.SkillsChosenMulti) -> None:
        """接收多技能选择事件，更新当前技能列表并合并工具白名单。"""
        try:
            names = list(message.names or [])
            skills = list(message.skills or [])
            self.current_skills = skills
            # 兼容：设置首个技能为 current_skill
            self.current_skill = skills[0] if skills else None

            # 合并工具白名单（并集），若存在至少一个白名单则采用合并结果
            merged_tools = set()
            has_any_whitelist = False
            for s in skills:
                m = getattr(s, "meta", None)
                if m and m.tools_whitelist:
                    has_any_whitelist = True
                    merged_tools.update(m.tools_whitelist)
            if has_any_whitelist:
                self.enabled_tools = merged_tools

            # 在聊天历史中加入系统提示，展示多技能选择摘要
            lines = ["已选择多个技能：" + (", ".join(names) if names else "<无>")]
            previews = []
            for s in skills[:6]:  # 预览前最多6个
                m = getattr(s, "meta", None)
                if not m:
                    continue
                previews.append(f"- {m.name}: {m.summary or ''}")
            if previews:
                lines.append("摘要预览：\n" + "\n".join(previews))
            if has_any_whitelist:
                lines.append("已合并白名单工具（并集应用）")
            chat_history = self.query_one("#chat-history", ChatHistoryWidget)
            chat_history.add_message("assistant", "\n".join(lines))
            self.notify(f"已选择{len(skills)}个技能", severity="success")
        except Exception as e:
            self.notify(f"处理多技能选择失败: {e}", severity="error")
    
    @on(ModelConfigModal.ConfigSaved)
    def on_model_config_saved(self, event: ModelConfigModal.ConfigSaved) -> None:
        """处理模型配置保存事件，转发给当前的 ModelConfigScreen"""
        # 添加调试信息
        self.notify("DEBUG: InteractiveChatApp.on_model_config_saved 被调用，准备转发给 ModelConfigScreen", severity="info")
        
        # 获取当前屏幕栈中的 ModelConfigScreen
        from .model_config_app import ModelConfigScreen
        for screen in reversed(self.screen_stack):
            if isinstance(screen, ModelConfigScreen):
                # 找到了 ModelConfigScreen，转发消息
                self.notify("DEBUG: 找到 ModelConfigScreen，转发 ConfigSaved 消息", severity="info")
                screen.on_config_saved(event)
                break
        else:
            self.notify("DEBUG: 未找到 ModelConfigScreen", severity="warning")
        
        # 刷新主界面的模型选择器
        try:
            model_selector = self.query_one(ModelSelectorWidget)
            model_selector.refresh_model_list()
            self.notify("DEBUG: 主界面模型选择器已刷新", severity="info")
        except Exception as e:
            self.notify(f"DEBUG: 刷新模型选择器失败: {e}", severity="warning")
        
    def action_focus_input(self) -> None:
        """聚焦到输入框"""
        input_widget = self.query_one("#message-input", CustomTextArea)
        input_widget.focus()
    
    def on_session_history_modal_session_selected(self, message) -> None:
        """处理历史会话选择事件"""
        self._load_session(message.session)
    
    def _load_session(self, session: ChatSession):
        """加载指定会话"""
        # 保存当前会话
        if self.current_session and self.conversation_history:
            self.current_session.messages = self.conversation_history.copy()
            self.session_manager.save_session(self.current_session)
        
        # 加载新会话
        self.current_session = session
        self.conversation_history = session.messages.copy()
        
        # 更新UI
        chat_history = self.query_one("#chat-history", ChatHistoryWidget)
        chat_history.clear_history()
        
        # 重新显示历史消息
        for message in self.conversation_history:
            if message["role"] == "user":
                chat_history.add_message("user", message["content"])
            elif message["role"] == "assistant":
                chat_history.add_message("assistant", message["content"])
        
        # 加载完成后提示一次
        self.notify(f"已加载会话: {session.get_display_title()}", severity="success")
    
    def _save_current_session(self):
        """保存当前会话
        
        将当前会话的消息历史和上下文保存到会话管理器中，
        确保会话状态在应用重启后能够恢复。
        """
        """保存当前会话"""
        if not self.conversation_history:
            return
        
        if not self.current_session:
            # 创建新会话
            self.current_session = ChatSession.create_new()
        
        # 更新会话消息
        self.current_session.messages = self.conversation_history.copy()
        self.current_session.updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 保存会话
        try:
            # 写入阶段5新增的步骤与工具记录
            steps_rec = getattr(self, "_session_step_records", [])
            tools_rec = getattr(self, "_session_tool_records", [])
            self.current_session.steps = steps_rec
            self.current_session.tools = tools_rec
        except Exception:
            pass
        self.session_manager.save_session(self.current_session)


def run_interactive_chat():
    """运行交互式对话应用"""
    import signal
    import sys
    import threading
    import concurrent.futures
    
    # 添加信号处理，确保程序可以正常退出
    def signal_handler(sig, frame):
        print("\n正在安全退出程序...")
        # 关闭所有线程池
        for executor in concurrent.futures._thread._global_shutdown_thread_pools:
            if hasattr(executor, '_threads'):
                for thread in executor._threads:
                    if thread is not None:
                        thread._tstate_lock = None
        # 退出程序
        sys.exit(0)
    
    # 注册信号处理器
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        app = InteractiveChatApp()
        app.run()
    except KeyboardInterrupt:
        print("\n检测到键盘中断，正在安全退出...")
        sys.exit(0)
    except Exception as e:
        print(f"交互式聊天应用启动失败: {e}")
        import traceback
        with open("interactive_chat_error.log", "w") as f:
            traceback.print_exc(file=f)
