from math import log
from typing import List, Dict, Any

import logging
import json
import hashlib
logger = logging.getLogger("ketacli.textual")

# 新增：基于内容指纹的去重，避免重复的大块文本进入上下文

def _fingerprint_text(text: str) -> str:
    try:
        return hashlib.sha256(text.encode("utf-8", "ignore")).hexdigest()[:16]
    except Exception:
        return str(len(text) or 0)


def _dedup_messages_by_content(existing: list, new_msgs: list, min_len: int = 400) -> list:
    """在追加新消息前进行去重：
    - 仅针对长度较大的消息（默认>=400字符），避免小提示被误杀
    - 比对 existing 中已存在内容的指纹，跳过重复
    """
    try:
        seen = set()
        for m in existing or []:
            c = (m.get("content") or "")
            if len(c) >= min_len:
                seen.add(_fingerprint_text(c))
        filtered = []
        for m in new_msgs or []:
            c = (m.get("content") or "")
            if len(c) < min_len:
                filtered.append(m)
                continue
            fp = _fingerprint_text(c)
            if fp in seen:
                try:
                    logger.debug(f"[dedup] 跳过重复消息 role={m.get('role')} len={len(c)} fp={fp}")
                except Exception:
                    pass
                continue
            seen.add(fp)
            filtered.append(m)
        return filtered
    except Exception:
        return new_msgs

from .ai_helpers import get_enabled_tools_openai_format, process_tool_calls, requires_user_confirmation, needs_tool_call
from .plan_executor import PlanExecutor
from ..widgets import ChatHistoryWidget, ModelSelectorWidget, ChatInputWidget
from ketacli.sdk.textual_chart.utils.history_utils import build_user_history_summary, build_user_raw_inputs_summary

# 统一标记常量与判定助手（重构）
# 新版标签（唯一选择、语义清晰）：
# - [STEP_NEXT]：当前步骤已完成，并明确给出下一步计划（推进）
# - [STEP_WAIT]：当前步骤未完成，需要用户确认/补充信息（暂停）
# - [STEP_BLOCKED]：外部系统/权限/资源问题导致无法继续（终止该步）
# - [TASK_DONE]：整个任务已完成（结束会话）
NEW_STEP_NEXT_MARKERS = {"[STEP_NEXT]", "[step_next]"}
NEW_STEP_WAIT_MARKERS = {"[STEP_WAIT]", "[step_wait]"}
NEW_STEP_BLOCKED_MARKERS = {"[STEP_BLOCKED]", "[step_blocked]"}
NEW_TASK_DONE_MARKERS = {"[TASK_DONE]", "[task_done]"}

# 兼容旧标签（保留识别，不在提示中再使用）：
DONE_MARKERS = {"[STEP_DONE]", "[step_done]", "步骤完成", "完成该步骤", "已完成该步骤"} | NEW_STEP_NEXT_MARKERS
CONTINUE_MARKERS = {"[STEP_CONTINUE]", "[step_continue]", "继续下一步", "需要继续", "继续执行", "继续"}
REQUIRE_USER_MARKERS = {"[STEP_REQUIRE_USER]", "[step_require_user]"} | NEW_STEP_WAIT_MARKERS

# 会话结束标记：扩展包含完成类中文短语与新任务完成标签
SESSION_DONE_MARKERS = {
    "[SESSION_DONE]", "[session_done]", "会话结束", "结束会话",
    "任务已完成", "任务完成", "对话完成",  "已完成任务"
} | NEW_TASK_DONE_MARKERS

# 完成类文本标记（用于无工具调用时的早停识别）
COMPLETE_MARKERS = {"任务已完成", "任务完成", "对话完成", "已完成任务"} | NEW_TASK_DONE_MARKERS


 

def safe_notify(app, message: str, severity: str = None, timeout: int = None, **kwargs) -> None:
    """安全通知包装：统一捕获通知异常，减少视觉噪音。"""
    try:
        notify = getattr(app, "notify", None)
        if callable(notify):
            if severity is not None:
                kwargs["severity"] = severity
            if timeout is not None:
                kwargs["timeout"] = timeout
            notify(message, **kwargs)
    except Exception:
        pass


def has_marker(text: str, markers: set) -> bool:
    try:
        lower = (text or "").lower()
    except Exception:
        lower = ""
    if not lower:
        return False
    return any((m or "").lower() in lower for m in (markers or set()))

# 新增：是否结束会话判定
def should_end_session(text: str, has_tool_calls: bool = False) -> bool:
    """判断是否应结束当前会话：
    - 若包含会话结束标记，直接结束；
    - 若存在工具调用，优先执行工具，不以 STEP_DONE 结束会话；
    - 若明确完成且未带继续标记，则结束会话。
    """
    try:
        # 1) 显式会话结束标记
        if has_marker(text, SESSION_DONE_MARKERS):
            return True
        # 2) 若无工具调用，且文本命中完成类标记，同时不包含继续/用户确认标记，则早停
        if (not has_tool_calls) and has_marker(text, COMPLETE_MARKERS):
            if (not has_marker(text, CONTINUE_MARKERS)) and (not should_pause_for_user(text)):
                return True
        return False
    except Exception:
        return False

def should_pause_for_user(text: str) -> bool:
    return bool(
        requires_user_confirmation(text)
        or has_marker(text, REQUIRE_USER_MARKERS)
        or has_marker(text, NEW_STEP_WAIT_MARKERS)
    )


def should_force_tool_call(app: Any, messages: List[Dict[str, Any]], user_text: str) -> bool:
    """统一的工具分支强制判定：
    - 若用户文本含“继续”语义标记，则强制走工具分支；
    - 若最近历史中存在 tool 角色消息（表示工具上下文仍在进行），也进入工具分支；
    - 若最近 assistant/user/system 文本出现继续语义，也进入工具分支。
    """
    try:
        if has_marker(user_text, CONTINUE_MARKERS):
            return True
        recent = messages[-6:] if messages else []
        for m in recent:
            if (m or {}).get("role") == "tool":
                return True
        for m in messages[-3:] if messages else []:
            if (m or {}).get("role") in ("assistant", "user", "system"):
                if has_marker((m or {}).get("content") or "", CONTINUE_MARKERS):
                    return True
    except Exception:
        return False
    return False


async def execute_task_steps(app: Any, steps: List[str], original_user_text: str) -> None:
    """执行任务步骤的通用流程，支持工具调用与总结标记。

    参数:
        app: 携带 UI/状态/AI 客户端的应用实例
        steps: 已规划的步骤列表
        original_user_text: 原始用户输入文本（用于上下文提示）
    """
    try:
        logger.debug(f"[steps] 启动步骤执行：数量={len(steps)}，原始文本长度={len(original_user_text or '')}")
    except Exception:
        pass
    # 标记计划状态为运行中
    try:
        setattr(app, "plan_status", "running")
    except Exception:
        pass

    # 保护性检查
    if not getattr(app, "ai_client", None):
        safe_notify(app, "AI客户端未初始化", severity="error")
        return

    # 获取 UI 组件（容错）
    try:
        chat_history = app.query_one("#chat-history", None)
        model_selector = app.query_one("#model-selector", None)
    except Exception:
        chat_history = None
        model_selector = None

    # 根据选择的模型刷新客户端（容错）
    try:
        selected_model = model_selector.get_selected_model() if model_selector else None
        if selected_model:
            app.ai_client = app.ai_client.__class__(
                system_prompt=getattr(app.ai_client, "system_prompt", ""),
                model_name=selected_model,
            )
        try:
            logger.debug(f"[steps] 当前选定模型={selected_model}；系统提示词长度={len(getattr(app.ai_client, 'system_prompt', '') or '')}")
        except Exception:
            pass
    except Exception:
        pass

    # 每步迭代上限（读取配置并限流）
    try:
        max_step_iterations = getattr(app.ai_client.model_config, "max_iterations", 8) or 8
        if not isinstance(max_step_iterations, int) or max_step_iterations <= 0:
            max_step_iterations = 8
        max_step_iterations = min(max_step_iterations, 8)
        try:
            logger.debug(f"[steps] 每步迭代上限={max_step_iterations}")
        except Exception:
            pass
    except Exception:
        max_step_iterations = 8

    # 完成/继续标记（统一常量）
    done_markers = DONE_MARKERS
    continue_markers = CONTINUE_MARKERS

    # 获取工具列表（容错）
    try:
        tools = get_enabled_tools_openai_format(getattr(app, "enabled_tools", {}))
        try:
            tool_names = [t.get("function", {}).get("name") for t in (tools or [])]
            logger.debug(f"[tools] 步骤执行工具：数量={len(tools)}；名称={tool_names}")
        except Exception:
            pass
    except Exception:
        tools = []
    # 新增：用于跨迭代去重工具调用的签名集合
    executed_tool_signatures = set()
    # 逐步执行
    for idx, step in enumerate(steps, start=1):
        try:
            if chat_history:
                chat_history.add_message("assistant", f"▶️ 开始执行第 {idx} 步：{step}")
            try:
                logger.debug(f"[step] 开始第{idx}步：内容长度={len(step or '')}")
            except Exception:
                pass

            # 基础消息（含严格标记提示）
            base_messages: List[Dict[str, Any]] = list(getattr(app, "conversation_history", []))
            # 仅收集用户曾经输入过的信息（公共方法解析摘要），排除当前输入与合成消息
            # 优先使用原始输入摘要，其次回退到会话历史
            try:
                _user_history_text = build_user_raw_inputs_summary(
                    getattr(app, "user_raw_inputs", []),
                    current_task_text=original_user_text,
                )
                if _user_history_text == "无":
                    _user_history_text = build_user_history_summary(
                        getattr(app, "conversation_history", []),
                        current_task_text=original_user_text,
                        exclude_synthetic=True,
                    )
            except Exception:
                _user_history_text = build_user_history_summary(
                    getattr(app, "conversation_history", []),
                    current_task_text=original_user_text,
                    exclude_synthetic=True,
                )
            try:
                logger.debug(f"[step] 上下文准备：历史消息={len(base_messages)}；用户历史摘要长度={len(_user_history_text or '')}")
            except Exception:
                pass

            base_messages.append({
                "role": "user",
                "synthetic": True,
                "content": (
                    f"用户当前任务：{original_user_text}\n"
                    f"用户历史输入：{_user_history_text}\n"
                    f"请严格执行以下步骤（第 {idx} 步）：{step}\n"
                    f"在回复最后一行添加一个标签（不要同时输出多个，也不要使用旧标签）：\n"
                    f"- 若本步已完成：添加标签 [STEP_NEXT]\n"
                    f"- 若本步需要继续执行：添加标签 [STEP_CONTINUE]\n"
                    f"- 若本步需要用户确认或补充参数：添加标签 [STEP_WAIT]\n"
                    f"- 若外部系统不可用/权限不足/资源缺失导致无法继续：添加标签 [STEP_BLOCKED]\n"
                    f"- 若整个任务已完成：添加标签 [TASK_DONE]\n"
                ),
            })
            try:
                _lim = 1200
                _synthetic_content = (base_messages[-1].get("content") or "")
                _preview = _synthetic_content if len(_synthetic_content) <= _lim else _synthetic_content[:_lim] + f"...[truncated {len(_synthetic_content)-_lim}]"
                logger.debug(f"[send][step {idx}] 追加synthetic user消息：预览={_preview}")
            except Exception:
                pass
            try:
                logger.debug(f"[step] 开始第{idx}步：内容长度={len(step or '')}")
            except Exception:
                pass

            # 步内迭代
            confirm_tried = False
            escalate_tried = False
            cont_streak = 0
            # 记录上一轮summary指纹，用于重复内容早停
            prev_summary_fp = ""
            for it in range(1, max_step_iterations + 1):
                try:
                    logger.debug(f"[iter] 第{idx}步迭代 {it}/{max_step_iterations}")
                except Exception:
                    pass

                # 在发起请求前，规范化并清洗工具消息，避免OpenAI 400
                try:
                    base_messages, _ra, _rt = await app._process_tool_sequence(base_messages)
                    try:
                        logger.debug(f"[tools][step {idx} iter {it}] 序列规范化：移除assistant={_ra}，移除tool={_rt}，消息数={len(base_messages)}")
                    except Exception:
                        pass
                    try:
                        provider = getattr(app.ai_client.model_config, "provider", "")
                        base_messages = app._sanitize_tool_messages(base_messages, provider)
                    except Exception:
                        pass
                except Exception:
                    pass

                # 助手响应（含工具）
                try:
                    # 发送前记录请求消息预览（取最近10条）
                    try:
                        _lim = 800
                        _payload_preview = []
                        for m in base_messages[-10:]:
                            _c = (m.get("content") or "")
                            _payload_preview.append({
                                "role": m.get("role"),
                                "content_preview": _c if len(_c) <= _lim else _c[:_lim] + f"...[truncated {len(_c)-_lim}]",
                            })
                        logger.debug(f"[send][step {idx} iter {it}] 请求消息预览：{json.dumps(_payload_preview, ensure_ascii=False, indent=2)}")
                    except Exception:
                        pass
                    response = await app.ai_client.chat_with_tools_async(
                        messages=base_messages,
                        tools=tools,
                        tool_choice="auto",
                    )
                except Exception as e:
                    if chat_history:
                        chat_history.add_message("assistant", f"❌ 工具阶段出错：{e}")
                    try:
                        logger.exception(f"[iter] 工具阶段调用异常：{e}")
                    except Exception:
                        pass
                    break

                assistant_msg = getattr(response, "content", "")
                tool_calls = getattr(response, "tool_calls", []) or []
 
                if assistant_msg:
                    if chat_history:
                        chat_history.add_message("assistant", assistant_msg)
                    # 追加前去重，避免重复的长文本assistant消息进入上下文
                    _new_assistant = _dedup_messages_by_content(base_messages, [{"role": "assistant", "content": assistant_msg}], min_len=600)
                    if _new_assistant:
                        base_messages.extend(_new_assistant)
                    # 若assistant消息已明确包含下一步标记，则直接判定当前步骤完成，跳过工具执行与总结
                    try:
                        assistant_next_hit = has_marker(assistant_msg, NEW_STEP_NEXT_MARKERS)
                        assistant_wait_hit = has_marker(assistant_msg, NEW_STEP_WAIT_MARKERS)
                        assistant_block_hit = has_marker(assistant_msg, NEW_STEP_BLOCKED_MARKERS)
                    except Exception:
                        assistant_next_hit = False
                        assistant_wait_hit = False
                        assistant_block_hit = False
                    if assistant_next_hit:
                        if chat_history:
                            chat_history.add_message("assistant", f"✅ 第 {idx} 步`({step})`完成（assistant新标签）")
                        try:
                            logger.debug(f"[step] 第{idx}步完成（assistant新标签），退出该步迭代")
                        except Exception:
                            pass
                        cont_streak = 0
                        # 保存会话历史后结束该步迭代
                        try:
                            app.conversation_history = base_messages
                            app._save_current_session()
                            try:
                                logger.debug(f"[step] 第{idx}步会话历史已保存：消息总数={len(base_messages)}")
                            except Exception:
                                pass
                        except Exception:
                            pass
                        break
                    # 新增：assistant直接指示暂停或阻塞时，立即暂停流程，等待用户交互
                    if assistant_wait_hit:
                        try:
                            logger.debug(f"[step] 第{idx}步暂停（assistant新标签 [STEP_WAIT]）")
                        except Exception:
                            pass
                        safe_notify(app, "⏸️ 暂停：需要你的输入或确认后继续。", timeout=4)
                        try:
                            app.conversation_history = base_messages
                            app._save_current_session()
                        except Exception:
                            pass
                        try:
                            setattr(app, "plan_status", "paused")
                        except Exception:
                            pass
                        return
                    if assistant_block_hit:
                        try:
                            logger.debug(f"[step] 第{idx}步阻塞（assistant新标签 [STEP_BLOCKED]）")
                        except Exception:
                            pass
                        safe_notify(app, "🛑 阻塞：外部条件限制，暂无法继续。", severity="error", timeout=4)
                        try:
                            app.conversation_history = base_messages
                            app._save_current_session()
                        except Exception:
                            pass
                        try:
                            setattr(app, "plan_status", "paused")
                        except Exception:
                            pass
                        return
                elif not tool_calls:
                    # 记录空响应以便触发提醒返回标签
                    try:
                        logger.debug(f"[iter] 模型assistant返回为空，将追加提示要求返回标签")
                    except Exception:
                        pass
                    empty_assistant_response = True
 
                # 过滤仅启用的工具调用
                # 过滤并去重工具调用（按启用工具 + 参数签名），避免重复调用导致无效循环
                try:
                    filtered_tool_calls, disabled_called_names, skipped_duplicates = await filter_and_deduplicate_tool_calls(app, tool_calls, executed_tool_signatures)
                    try:
                        logger.debug(f"[tools][step {idx} iter {it}] 过滤与去重：保留={len(filtered_tool_calls)}，忽略未启用={len(disabled_called_names)}")
                    except Exception:
                        pass
                except Exception:
                    # 回退：仅按启用工具名过滤
                    enabled_attr = getattr(app, "enabled_tools", None)
                    if isinstance(enabled_attr, dict):
                        enabled_names = set(enabled_attr.keys())
                    elif isinstance(enabled_attr, (set, list, tuple)):
                        enabled_names = set(enabled_attr)
                    else:
                        enabled_names = set()
                    filtered_tool_calls = [
                        tc for tc in (tool_calls or []) if tc.get("function", {}).get("name") in enabled_names
                    ]
                    disabled_called_names = []

                # 将重复调用跳过信息反馈到上下文，指导模型避免重复
                try:
                    if locals().get("skipped_duplicates"):
                        dup_preview = ", ".join([(d or {}).get("name") or "" for d in (skipped_duplicates or []) if (d or {}).get("name")][:6])
                        if dup_preview.strip():
                            base_messages.append({
                                "role": "user",
                                "synthetic": True,
                                "content": (
                                    f"提示：重复的工具调用已被跳过（按参数签名去重）：{dup_preview}。"
                                    f"请避免对同一参数重复调用，优先调整参数或继续思考再尝试。"
                                ),
                            })
                            try:
                                logger.debug(f"[tools][step {idx} iter {it}] 重复调用提示已追加到上下文：{dup_preview}")
                            except Exception:
                                pass
                except Exception:
                    pass

                # 确保按 OpenAI 规范：若存在工具调用，前置 assistant 消息必须携带 tool_calls
                if filtered_tool_calls:
                    if base_messages and (base_messages[-1].get("role") == "assistant"):
                        # 将最近的 assistant 消息补充上 tool_calls
                        base_messages[-1]["tool_calls"] = filtered_tool_calls
                        # 若无文本内容，保持为空字符串即可
                        if "content" not in base_messages[-1]:
                            base_messages[-1]["content"] = assistant_msg or ""
                    else:
                        base_messages.append({
                            "role": "assistant",
                            "content": assistant_msg or "",
                            "tool_calls": filtered_tool_calls,
                        })

                # 执行工具调用并附加消息
                tool_messages = []
                try:
                    tool_messages = await process_tool_calls(
                        filtered_tool_calls,
                        chat_history_widget=chat_history,
                        add_to_base_messages=True,
                    )
                except Exception as e:
                    if chat_history:
                        chat_history.add_message("assistant", f"⚠️ 处理工具调用失败：{e}")
                    try:
                        logger.exception(f"[tools] 工具调用处理异常：{e}")
                    except Exception:
                        pass
                # 工具执行后的预览与统计日志
                try:
                    _lim = 1500
                    _tm_preview = [{
                        "role": tm.get("role"),
                        "content_preview": (tm.get("content") or "") if len(tm.get("content") or "") <= _lim else (tm.get("content") or "")[:_lim] + f"...[truncated {len(tm.get('content') or '')-_lim}]",
                    } for tm in (tool_messages or [])]
                    logger.debug(f"[recv][step {idx} iter {it}] tool消息：{_tm_preview}")
                except Exception:
                    pass
                try:
                    logger.debug(f"[tools] 工具执行完成：追加消息数={len(tool_messages or [])}")
                except Exception:
                    pass
                # 在追加前进行内容去重，避免重复的文档/长文本反复进入上下文
                tool_messages = _dedup_messages_by_content(base_messages, tool_messages, min_len=600)
                base_messages.extend(tool_messages or [])
                

            # 总结与完成判定（无论工具是否异常，均进入总结阶段）
            # 发送前记录总结请求消息预览（取最近10条）
            try:
                _lim = 800
                _payload_preview = []
                for m in base_messages[-10:]:
                    _c = (m.get("content") or "")
                    _payload_preview.append({
                        "role": m.get("role"),
                        "content_preview": _c if len(_c) <= _lim else _c[:_lim] + f"...[truncated {len(_c)-_lim}]",
                    })
                logger.debug(f"[send][step {idx} iter {it}] 总结请求消息预览：{json.dumps(_payload_preview, ensure_ascii=False, indent=2)}")
            except Exception:
                pass
            # 若上一轮assistant为空，则直接提醒模型返回标签
            try:
                if 'empty_assistant_response' in locals() and empty_assistant_response:
                    synth_prompt = {
                        "role": "user",
                        "synthetic": True,
                        "content": (
                            f"刚才你的回复为空。请输出总结并判断第 {idx} 步状态：\n"
                            f"已完成在文本末添加 [STEP_DONE]，未完成添加 [STEP_CONTINUE]，若整体任务完成添加 [SESSION_DONE]。\n"
                            f"如工具执行未返回预期结果，请重新整理工具需要的参数后继续执行；并在总结结尾添加[STEP_CONTINUE]"
                        ),
                    }
                    base_messages.append(synth_prompt)
                    confirm_tried = True
                    try:
                        logger.debug(f"[send][step {idx} iter {it}] 追加标签提醒提示：{synth_prompt.get('content')}")
                    except Exception:
                        pass
                    empty_assistant_response = False
            except Exception:
                pass
            try:
                logger.debug(f"[send][step {idx} iter {it}] 发送消息上下文：{json.dumps(base_messages, ensure_ascii=False, indent=2)}")
                summary = await app.ai_client.chat_async(base_messages)
                
            except Exception as e:
                if chat_history:
                    chat_history.add_message("assistant", f"❌ 总结阶段出错：{e}")
                break

            summary_text = getattr(summary, "content", "") or ""
            logger.debug(f"[recv][step {idx} iter {it}] 模型回复：{json.dumps(summary_text, ensure_ascii=False, indent=2)}")
            try:
                _lim = 2000
                _sum_preview = summary_text if len(summary_text or "") <= _lim else summary_text[:_lim] + f"...[truncated {len(summary_text)-_lim}]"
                logger.debug(f"[recv][step {idx} iter {it}] summary/confirm：预览={_sum_preview}")
            except Exception:
                pass
            try:
                logger.debug(f"[summary] 长度={len(summary_text or '')}；需用户确认={requires_user_confirmation(summary_text)}")
            except Exception:
                pass
            # 若需要用户确认/补全，确保追加标记
            if requires_user_confirmation(summary_text) and not has_marker(summary_text, REQUIRE_USER_MARKERS):
                sep = "\n\n" if not summary_text.endswith("\n") else "\n"
                summary_text = summary_text + sep + "[STEP_REQUIRE_USER]"
            # 将总结加入历史与基消息
            if chat_history and summary_text:
                chat_history.add_message("assistant", summary_text)
            base_messages.append({"role": "assistant", "content": summary_text})

            # 需要用户确认时暂停会话
            if should_pause_for_user(summary_text):
                try:
                    logger.debug(f"[step] 第{idx}步暂停：等待用户输入/确认")
                except Exception:
                    pass
                safe_notify(app, "⏸️ 暂停：等待你的输入或确认后继续。", timeout=4)
                try:
                    app.conversation_history = base_messages
                    app._save_current_session()
                except Exception:
                    pass
                # 记录计划状态为暂停
                try:
                    setattr(app, "plan_status", "paused")
                except Exception:
                    pass
                return

            # 会话结束标记（含新旧任务完成标签）
            # 防止在非末步收到 [TASK_DONE] / [SESSION_DONE] 导致提前结束整个会话
            force_continue = False
            try:
                total_steps = len(steps)
            except Exception:
                total_steps = 0
            try:
                # 非末步：当前步序号小于总步数（例如总5步，则1~4为非末步）
                is_mid_step = idx < total_steps
            except Exception:
                is_mid_step = False
            try:
                # 若在非末步出现“任务完成”相关标记或短语，强制继续后续步骤，避免提前结束整个会话
                task_done_midway = is_mid_step and (
                    has_marker(summary_text, NEW_TASK_DONE_MARKERS)
                    or has_marker(summary_text, SESSION_DONE_MARKERS)
                    or has_marker(summary_text, COMPLETE_MARKERS)
                )
            except Exception:
                task_done_midway = False

            if task_done_midway:
                # 非末步收到任务完成标签/短语——按推进处理，继续后续步骤
                force_continue = True
                try:
                    logger.debug(f"[step] 非末步收到任务完成相关标记，按 [STEP_NEXT] 继续到第{idx+1}步")
                except Exception:
                    pass
                if chat_history:
                    chat_history.add_message("assistant", f"ℹ️ 收到任务完成相关标记但尚有后续步骤，继续执行第 {idx+1} 步。")

            # 若刚执行过工具或处于非末步，则不应因完成短语提前结束会话
            try:
                _has_tool_calls = bool(locals().get("tool_executed", False))
            except Exception:
                _has_tool_calls = False
            # 仅在“最后一步”且命中会话结束标记时才允许结束会话；
            # 在非末步一律不因完成短语/标记而早停。
            try:
                is_last_step = idx >= total_steps and total_steps > 0
            except Exception:
                is_last_step = False
            if (not force_continue) and is_last_step and should_end_session(summary_text, has_tool_calls=_has_tool_calls):
                try:
                    logger.debug("[step] 会话结束标记命中，退出步骤执行")
                except Exception:
                    pass
                safe_notify(app, "✅ 会话完成", timeout=4)
                try:
                    app.conversation_history = base_messages
                    app._save_current_session()
                except Exception:
                    pass
                # 标记计划状态为完成
                try:
                    setattr(app, "plan_status", "completed")
                except Exception:
                    pass
                return

            # 额外检测：仅返回标记与外部系统阻塞
            stripped = (summary_text or "").strip()
            only_marker = stripped in (
                "[STEP_NEXT]", "[STEP_WAIT]", "[STEP_BLOCKED]", "[TASK_DONE]",
                "[STEP_DONE]", "[STEP_CONTINUE]", "[SESSION_DONE]", "[STEP_REQUIRE_USER]"
            )
            blocked_keywords = [
                "系统不可用", "平台超时", "持续超时", "超时", "权限不足", "没有权限", "无权限",
                "资源缺失", "资源不存在", "不可访问", "无法执行", "执行失败", "失败",
                "服务不可用", "不可用", "受限", "限制", "quota", "rate limit", "连接错误",
            ]
            blocked_by_system = any(k in (summary_text or "") for k in blocked_keywords)

            # 原始标记判定
            done_hit = has_marker(summary_text, DONE_MARKERS)
            cont_hit = has_marker(summary_text, CONTINUE_MARKERS)
            # 放宽启发式完成：只要明确指向下一步，则视为当前步完成
            auto_done = mentions_next_step(summary_text, idx)
            try:
                logger.debug(f"[step] 标记状态：DONE={done_hit} CONTINUE={cont_hit} AUTO_DONE={auto_done}")
            except Exception:
                pass

            # 若已执行工具且总结明确给出下一步/自然阻塞，也视为本步完成（避免同一步反复重试）
            try:
                tool_executed = bool(locals().get("tool_messages")) and len(locals().get("tool_messages") or []) > 0
            except Exception:
                tool_executed = False

            # 新标签命中与旧标签兼容
            next_hit = has_marker(summary_text, NEW_STEP_NEXT_MARKERS)
            blocked_hit = has_marker(summary_text, NEW_STEP_BLOCKED_MARKERS)
            task_done_hit = has_marker(summary_text, NEW_TASK_DONE_MARKERS) or has_marker(summary_text, SESSION_DONE_MARKERS)

            if task_done_hit and not (locals().get("force_continue", False)):
                # 任务完成：在上方 should_end_session 已处理；此处防御性补充
                try:
                    logger.debug(f"[step] 检测到任务完成标签，触发会话结束")
                except Exception:
                    pass
                safe_notify(app, "✅ 会话完成", timeout=4)
                try:
                    app.conversation_history = base_messages
                    app._save_current_session()
                except Exception:
                    pass
                try:
                    setattr(app, "plan_status", "completed")
                except Exception:
                    pass
                return

            # 若检测到工具失败，则禁止进入下一步，强制在本步继续（忽略 [STEP_NEXT] 与启发式完成）
            if locals().get("tool_failed", False):
                try:
                    logger.debug(f"[step] 检测到工具失败，忽略下一步标记，继续当前步骤")
                except Exception:
                    pass
                # 追加一次明确的重试提示，避免模型误判本步已完成
                retry_prompt = {
                    "role": "user",
                    "synthetic": True,
                    "content": (
                        f"请在当前步骤中先获取必要的文档与上下文（例如字段结构、SPL语法规范、参数示例），然后修正参数并重试工具调用。\n"
                        f"完成这些操作后，在总结的最后一行仅输出 [STEP_CONTINUE]。"
                    ),
                }
                base_messages.append(retry_prompt)
                cont_streak = 0
                # 不退出该步迭代，继续向模型请求更具体的操作
            elif next_hit or (done_hit and not cont_hit) or auto_done:
                if chat_history:
                    chat_history.add_message("assistant", f"✅ 第 {idx} 步`({step})`完成")
                try:
                    logger.debug(f"[step] 第{idx}步完成（{'新标签' if next_hit else ('显式' if done_hit else '启发式')}），退出该步迭代")
                except Exception:
                    pass
                cont_streak = 0
                break
            elif blocked_hit and blocked_by_system:
                # 外部阻塞：终止该步并提示
                if chat_history:
                    chat_history.add_message("assistant", f"⛔ 第 {idx} 步`({step})`因外部阻塞而终止（[STEP_BLOCKED]）")
                try:
                    logger.debug(f"[step] 第{idx}步外部阻塞，终止该步迭代")
                except Exception:
                    pass
                cont_streak = 0
                break
            elif tool_executed and (mentions_next_step(summary_text, idx)):
                # 工具执行后明确进入下一步，直接判定为完成
                if chat_history:
                    chat_history.add_message("assistant", f"✅ 第 {idx} 步`({step})`完成（工具已执行并给出下一步）")
                try:
                    logger.debug(f"[step] 第{idx}步完成（工具后启发式）")
                except Exception:
                    pass
                cont_streak = 0
                break
            else:
                # 若首轮未命中标记，追加一次最小确认以获取显式标记
                if not confirm_tried and it == 1:
                    confirm_msg = {
                        "role": "user",
                        "synthetic": True,
                        "content": (
                            f"请在回复最后一行仅输出一个标签，不要同时输出多个：\n"
                            f"- 第 {idx} 步已完成并给出下一步：仅输出 [STEP_NEXT]\n"
                            f"- 需要你的确认或补充参数：仅输出 [STEP_WAIT]\n"
                            f"- 外部系统不可用/权限不足/资源缺失：仅输出 [STEP_BLOCKED]\n"
                            f"- 整个任务已完成：仅输出 [TASK_DONE]"
                        ),
                    }
                    base_messages.append(confirm_msg)
                    try:
                        logger.debug(f"[send][step {idx} iter {it}] 追加确认标记请求")
                    except Exception:
                        pass
                    try:
                        confirm_resp = await app.ai_client.chat_async(base_messages)
                        confirm_text = getattr(confirm_resp, "content", "") or ""
                        _lim = 200
                        _cprev = confirm_text if len(confirm_text) <= _lim else confirm_text[:_lim] + f"...[truncated {len(confirm_text)-_lim}]"
                        logger.debug(f"[recv][step {idx} iter {it}] confirm：{_cprev}")
                    except Exception:
                        confirm_text = ""
                    if chat_history and confirm_text.strip():
                        chat_history.add_message("assistant", confirm_text)
                    base_messages.append({"role": "assistant", "content": confirm_text})
                    confirm_tried = True
                    # 重新判定标记
                    done_hit = has_marker(confirm_text, DONE_MARKERS)
                    cont_hit = has_marker(confirm_text, CONTINUE_MARKERS)
                    try:
                        logger.debug(f"[step] 标记确认：DONE={done_hit} CONTINUE={cont_hit}")
                    except Exception:
                        pass
                    if done_hit and not cont_hit:
                        if chat_history:
                            chat_history.add_message("assistant", f"✅ 第 {idx} 步`({step})`完成")
                        cont_streak = 0
                        break
                    # 若明确继续则进入下一轮
                    if cont_hit:
                        cont_streak += 1
                        if chat_history:
                            chat_history.add_message("assistant", f"↻ 第 {idx} 步`({step})`继续迭代（{it}/{max_step_iterations}）")
                        try:
                            logger.debug(f"[step] 第{idx}步继续迭代（{it}/{max_step_iterations}），streak={cont_streak}")
                        except Exception:
                            pass
                        continue
                # 默认继续迭代（非首轮或确认后仍需继续）
                # 计算当前summary指纹，基于重复内容进行早停保护
                try:
                    cur_fp = _fingerprint_text(summary_text)
                except Exception:
                    cur_fp = ""
                if cont_hit:
                    cont_streak += 1
                else:
                    cont_streak = 0
                # 迭代保护：若连续两轮继续且总结内容未变化，且文本明确进入下一步，则视为完成
                try:
                    if cont_streak >= 2 and prev_summary_fp and (cur_fp == prev_summary_fp) and mentions_next_step(summary_text, idx):
                        if chat_history:
                            chat_history.add_message("assistant", f"✅ 第 {idx} 步`({step})`完成（重复迭代保护触发）")
                        logger.debug(f"[step] 第{idx}步重复迭代保护早停：streak={cont_streak}")
                        cont_streak = 0
                        break
                except Exception:
                    pass
                prev_summary_fp = cur_fp
                if chat_history:
                    chat_history.add_message("assistant", f"↻ 第 {idx} 步`({step})`继续迭代（{it}/{max_step_iterations}）")
                try:
                    logger.debug(f"[step] 第{idx}步继续迭代（{it}/{max_step_iterations}），streak={cont_streak}")
                except Exception:
                    pass
                
                continue

            # 更新对话历史并保存
            try:
                app.conversation_history = base_messages
                app._save_current_session()
                try:
                    logger.debug(f"[step] 第{idx}步会话历史已保存：消息总数={len(base_messages)}")
                except Exception:
                    pass
            except Exception:
                pass

        except Exception as e:
            if chat_history:
                chat_history.add_message("assistant", f"❌ 执行第 {idx} 步失败：{e}")
            try:
                logger.exception(f"[step] 执行第{idx}步失败：{e}")
            except Exception:
                pass
            continue

    # 完成提示
    safe_notify(app, f"🧭 {len(steps)} 个步骤执行结束", timeout=3)
    try:
        logger.debug(f"[steps] 步骤执行结束：总步骤数={len(steps)}")
    except Exception:
        pass
    # 标记计划状态为完成
    try:
        setattr(app, "plan_status", "completed")
    except Exception:
        pass


async def process_ai_response(app: Any, user_message: str, streaming: bool = None) -> None:
    """通用的 AI 响应处理流程：准备上下文、规划步骤、工具迭代与收尾。"""
    if not getattr(app, "ai_client", None):
        safe_notify(app, "AI客户端未初始化", severity="error")
        return

    # 若未显式传入，则从应用或模型配置读取，默认启用流式
    if streaming is None:
        try:
            streaming = getattr(app, "enable_streaming", None)
        except Exception:
            streaming = None
        if streaming is None:
            try:
                # 先读取直接字段
                streaming = bool(getattr(app.ai_client.model_config, "streaming", False))
                # 再尝试 extra_params 中的 streaming / enable_streaming / stream
                extra = getattr(app.ai_client.model_config, "extra_params", {}) or {}
                for key in ("streaming", "enable_streaming", "stream"):
                    if key in extra:
                        streaming = bool(extra.get(key))
                        break
            except Exception:
                safe_notify(app, "读取流式配置失败，默认启用流式", severity="warning")
                streaming = False

    # 调试：记录流式配置
    logger.debug(f"[flow] streaming配置：{streaming}")
    # 标记进程进行中
    app._chat_in_progress = True
    try:
        chat_history = app.query_one("#chat-history", ChatHistoryWidget)
        model_selector = app.query_one("#model-selector", ModelSelectorWidget)
    except Exception:
        chat_history = None
        model_selector = None

    try:
        # 增强系统提示词
        try:
            app.ai_client.system_prompt = app._augment_system_prompt(app.ai_client.system_prompt)
            logger.debug(f"[prompt] 系统提示词长度={len(app.ai_client.system_prompt or '')}")
        except Exception:
            pass

        # 准备消息
        messages = app._prepare_messages(user_message)
        logger.debug(f"[context] 准备完成：消息数={len(messages)}")

        # 若存在计划执行中，则跳过重新规划，转入普通回复流程
        try:
            if getattr(app, "plan_execution_in_progress", False) or getattr(app, "planning_locked", False):
                logger.debug("[plan] 会话规划已锁定或执行中，跳过新的规划。")
            else:
                # 自动任务规划（返回 dict，包括 type 与 steps）
                try:
                    logger.debug(f"[plan] 原始需求={user_message}")
                    plan = await app._plan_task_steps(user_message)
                    logger.debug(f"[plan] 自动规划={plan}")
                except Exception as e:
                    logger.error(f"生成任务步骤失败：{e}。原始需求：{user_message}")
                    safe_notify(app, f"生成任务步骤失败。原始需求：{user_message}", severity="error")
                    plan = {"type": "task", "complexity": "low", "steps": [user_message]}

                # 若为任务且有步骤，先展示规划并委托步骤执行；问题类型则直接继续正常响应流程
                steps = (plan.get("steps") or []) if isinstance(plan, dict) else []
                # 注入规划生成的系统提示（若有），用于引导后续执行阶段
                try:
                    custom_sys_prompt = str((plan.get("system_prompt") or "").strip()) if isinstance(plan, dict) else ""
                except Exception:
                    custom_sys_prompt = ""
                if custom_sys_prompt:
                    try:
                        base_prompt = app.ai_client.system_prompt or ""
                        merged_prompt = f"{base_prompt}\n\n{custom_sys_prompt}".strip()
                        app.ai_client.system_prompt = app._augment_system_prompt(merged_prompt)
                        logger.debug(f"[prompt] 已注入规划system_prompt，长度={len(app.ai_client.system_prompt or '')}")
                    except Exception:
                        pass
                if isinstance(plan, dict) and (plan.get("type") == "task") and len(steps) > 0:
                    try:
                        plan_text = "\n".join([f"{i+1}. {s}" for i, s in enumerate(steps)])
                        if chat_history:
                            chat_history.add_message("assistant", f"🧭 已拆分为{len(steps)}个步骤：\n{plan_text}")
                    except Exception:
                        pass
                    # 设置规划执行状态并锁定本会话规划，防止新的消息触发重复规划
                    try:
                        setattr(app, "planning_locked", True)
                        setattr(app, "plan_execution_in_progress", True)
                        logger.debug("[plan] 已锁定会话规划，并标记执行中=True")
                    except Exception:
                        pass
                    try:
                        executor = PlanExecutor()
                        await executor.run(app, steps, user_message)
                    finally:
                        try:
                            status = getattr(app, "plan_status", None)
                            if status == "completed":
                                setattr(app, "plan_execution_in_progress", False)
                            else:
                                # 仍处于暂停或运行中，保持锁以避免重复规划
                                setattr(app, "plan_execution_in_progress", True)
                        except Exception:
                            pass
                    return
        except Exception:
            # 若状态判定流程异常，不阻断后续普通回复逻辑
            pass

        # 规范化工具消息顺序
        messages, removed_assistant, removed_tool = app._enforce_openai_tool_sequence(messages)
        logger.debug(f"[tools] 序列规范化：移除assistant={removed_assistant}，移除tool={removed_tool}，消息数={len(messages)}")
        if removed_assistant or removed_tool:
            safe_notify(
                app,
                f"🧹 已规范化工具消息：移除不完整assistant {removed_assistant} 条/孤立tool {removed_tool} 条",
                severity="warning",
                timeout=4,
            )

        # 获取可用工具
        tools = app._get_enabled_tools_openai_format()
        logger.debug(f"[tools] 可用工具数量={len(tools)}")
        try:
            provider = getattr(app.ai_client.model_config, "provider", "")
            current_model = app.ai_client.get_current_model() if hasattr(app.ai_client, "get_current_model") else ""
            safe_notify(app, f"🔧 当前模型: {current_model} / 提供方: {provider}，可用工具: {len(tools)}", timeout=3)
            force_tools_branch = should_force_tool_call(app, messages, user_message)
            if force_tools_branch:
                safe_notify(app, "➡️ 已因‘继续’与历史工具调用，强制走工具分支", timeout=4)
        except Exception:
            safe_notify(app, "🔧 获取可用工具失败，默认使用20次迭代", severity="warning", timeout=3)

        # 新增：在进入工具分支前进行 needs_tool_call 判定，避免无意义迭代
        try:
            if not force_tools_branch and not needs_tool_call(user_message):
                # 走普通对话路径，避免工具迭代
                from .chat_stream import stream_chat_async
                from ..token_calculator import calculate_token_stats
                # 流式或非流式处理
                if streaming:
                    try:
                        chat_history = app.query_one("#chat-history", ChatHistoryWidget)
                    except Exception:
                        chat_history = None
                    streaming_widget = chat_history.start_streaming_message("assistant") if chat_history else None
                    accumulated = ""
                    try:
                        async for chunk in stream_chat_async(app, messages):
                            content = chunk if isinstance(chunk, str) else (chunk.get("content") if isinstance(chunk, dict) else str(chunk))
                            content = content or ""
                            accumulated += content
                            try:
                                if streaming_widget:
                                    streaming_widget.append_content(content)
                            except Exception:
                                pass
                    except Exception:
                        # 回退到非流式
                        try:
                            resp = await app.ai_client.chat_async(messages)
                            accumulated = getattr(resp, "content", "") or ""
                        except Exception:
                            accumulated = ""
                    # 完成并追加消息
                    assistant_msg_dict = {"role": "assistant", "content": accumulated}
                    messages.append(assistant_msg_dict)
                    if chat_history:
                        message_added = chat_history.finish_streaming_message(accumulated)
                        if not message_added:
                            context_for_assistant = messages[:-1] if messages else []
                            token_stats = calculate_token_stats(current_message=assistant_msg_dict, context_messages=context_for_assistant)
                            chat_history.add_message("assistant", accumulated, token_stats=token_stats)
                    app.conversation_history = messages
                    return
                else:
                    try:
                        resp = await app.ai_client.chat_async(messages)
                        content = getattr(resp, "content", "") or ""
                    except Exception:
                        content = ""
                    assistant_msg_dict = {"role": "assistant", "content": content}
                    messages.append(assistant_msg_dict)
                    try:
                        chat_history = app.query_one("#chat-history", ChatHistoryWidget)
                    except Exception:
                        chat_history = None
                    if chat_history:
                        context_for_assistant = messages[:-1] if messages else []
                        token_stats = calculate_token_stats(current_message=assistant_msg_dict, context_messages=context_for_assistant)
                        chat_history.add_message("assistant", content, token_stats=token_stats)
                    app.conversation_history = messages
                    return
        except Exception:
            # 判定失败不影响后续工具流程
            pass

        # 迭代上限（用于流控信息展示）
        try:
            max_iterations = getattr(app.ai_client.model_config, "max_iterations", 20) or 20
            if not isinstance(max_iterations, int) or max_iterations <= 0:
                max_iterations = 20
        except Exception:
            max_iterations = 20

        # 运行工具迭代（委托到公共实现）
        logger.debug(f"[iteration] 准备迭代：streaming={streaming}，上限={max_iterations}，消息数={len(messages)}，工具数={len(tools)}")
        result = await run_tool_iterations(app, messages, tools, user_message, streaming=streaming)
        messages = result.get("messages", messages)
        app.conversation_history = messages
        return

    except Exception as e:
        logger.exception(f"[flow] 处理请求异常: {type(e).__name__}: {e}")
        try:
            if chat_history:
                chat_history.add_message("assistant", f"❌ 处理请求时出错: {str(e)}")
        except Exception:
            pass
    finally:
        app._chat_in_progress = False
        app._current_ai_task = None
        try:
            chat_input = app.query_one("#chat-input", ChatInputWidget)
            chat_input.set_loading(False)
            chat_input.set_processing(False)
        except Exception:
            pass
        # 自动保存会话
        try:
            app._save_current_session()
        except Exception:
            pass


async def filter_and_deduplicate_tool_calls(app, tool_calls: list, executed_tool_signatures: set) -> tuple:
    """过滤和去重工具调用，返回(过滤后的调用列表, 被忽略的未启用工具名列表, 跳过的重复调用信息列表)。"""
    filtered_tool_calls = []
    disabled_called_names = []
    skipped_duplicates = []
    try:
        enabled = set(getattr(app, "enabled_tools", set()) or set())
        # 只保留启用工具的调用
        filtered_tool_calls = [
            tc for tc in (tool_calls or [])
            if ((tc or {}).get("function", {}).get("name") in enabled)
        ]
        # 根据函数名+规范化参数做去重
        try:
            import json
            dedup = []
            for tc in filtered_tool_calls:
                fn = (tc or {}).get("function", {})
                nm = fn.get("name")
                args = fn.get("arguments", "{}")
                try:
                    if isinstance(args, (dict, list)):
                        args_norm = json.dumps(args, ensure_ascii=False, sort_keys=True)
                    else:
                        args_norm = str(args)
                except Exception:
                    args_norm = str(args)
                sig = f"{nm}:{args_norm}"
                if sig in executed_tool_signatures:
                    safe_notify(app, f"♻️ 跳过重复工具调用: {nm}", severity="warning", timeout=3)
                    # 记录重复调用信息用于后续追加到上下文
                    try:
                        skipped_duplicates.append({
                            "name": nm or "",
                            "arguments": args_norm,
                            "tool_call_id": (tc or {}).get("id") or "",
                        })
                    except Exception:
                        pass
                    continue
                executed_tool_signatures.add(sig)
                dedup.append(tc)
            filtered_tool_calls = dedup
        except Exception:
            pass
        # 收集未启用工具名
        try:
            disabled_called_names = [
                (tc or {}).get("function", {}).get("name")
                for tc in (tool_calls or [])
                if ((tc or {}).get("function", {}).get("name") not in enabled)
            ]
            if disabled_called_names:
                try:
                    preview = ", ".join([n for n in disabled_called_names if n][:6])
                    safe_notify(
                        app,
                        f"🚫 检测到未启用的工具调用已被忽略：{preview}",
                        severity="warning",
                        timeout=4,
                    )
                except Exception:
                    pass
        except Exception:
            pass
    except Exception:
        filtered_tool_calls = []
    return filtered_tool_calls, disabled_called_names, skipped_duplicates


async def run_tool_iterations(app, messages: list, tools: list, user_message: str, streaming: bool = True) -> dict:
    """运行工具调用迭代（公共实现），支持流式/非流式两种模式。"""
    iteration = 0
    block_tool_retry_for_current_query = False
    executed_tool_signatures = set()
    # 新增：记录上一轮助手文本，用于重复内容早停
    previous_assistant_text = ""

    # 迭代上限
    try:
        max_iterations = getattr(app.ai_client.model_config, "max_iterations", 20) or 20
        if not isinstance(max_iterations, int) or max_iterations <= 0:
            max_iterations = 20
    except Exception:
        max_iterations = 20

    # UI 组件
    try:
        from ..widgets import ChatHistoryWidget
        chat_history = app.query_one("#chat-history", ChatHistoryWidget)
    except Exception:
        chat_history = None
    streaming_widget = chat_history.start_streaming_message("assistant") if (chat_history and streaming) else None

    # 依赖函数（避免顶部改动，内部导入）
    from .chat_stream import process_tool_sequence, stream_and_process_response
    from ..token_calculator import calculate_token_stats
    from ketacli.sdk.ai.function_call import function_executor
    from ketacli.sdk.ai.tool_output_compressor import compress_if_large
    from textual.widget import Widget
    from .ai_helpers import plan_task_steps, requires_user_confirmation

    while iteration < max_iterations:
        iteration += 1
        safe_notify(app, f"➡️ 第{iteration}轮工具请求，上下文消息数: {len(messages)}", timeout=2)

        # 处理工具调用序列，规范化消息历史
        messages, ra, rt = await process_tool_sequence(app, messages)

        # 获取AI响应：根据模式选择流式或非流式
        if streaming:
            response, _ = await stream_and_process_response(app, messages, tools, streaming_widget)
        else:
            try:
                response = await app.ai_client.chat_with_tools_async(messages=messages, tools=tools)
            except Exception:
                # 回退到普通回答
                try:
                    response = await app.ai_client.chat_async(messages)
                except Exception:
                    class _EmptyResp:
                        content = ""
                        tool_calls = []
                    response = _EmptyResp()

        # 构造助手消息
        assistant_message = {"role": "assistant", "content": getattr(response, "content", "")}
        try:
            logger.debug(f"[iteration] 模型响应：content_len={len(getattr(response,'content','') or '')}，tool_calls={len(getattr(response,'tool_calls',[]) or [])}")
        except Exception:
            pass

        # 过滤与去重工具调用
        filtered_tool_calls, disabled_called_names, skipped_duplicates = await filter_and_deduplicate_tool_calls(
            app, (getattr(response, "tool_calls", None) or []), executed_tool_signatures
        )
        try:
            logger.debug(f"[iteration] 工具调用过滤：保留={len(filtered_tool_calls)}，忽略未启用={len(disabled_called_names)}")
        except Exception:
            pass

        # 处理禁用工具提示与空内容回退
        try:
            if disabled_called_names:
                try:
                    preview = ", ".join([n for n in disabled_called_names if n][:6])
                    guidance = (
                        f"⚠️ 检测到模型尝试调用未启用的工具：{preview}。该调用已被忽略。\n"
                        "请按 `T` 或 `Ctrl+T` 打开工具列表启用所需工具，或继续输入让我在不使用工具的情况下回答。"
                    )
                    existing = (assistant_message.get("content") or "")
                    if existing.strip():
                        sep = "\n\n" if not existing.endswith("\n") else "\n"
                        assistant_message["content"] = existing + sep + guidance
                    else:
                        assistant_message["content"] = guidance
                except Exception:
                    pass
            if (not filtered_tool_calls) and disabled_called_names and not (assistant_message.get("content") or "").strip():
                disabled_preview = ", ".join([n for n in disabled_called_names if n][:6])
                fallback_text = (
                    f"⚠️ 检测到模型尝试调用未启用的工具：{disabled_preview}。该调用已被忽略。\n"
                    "请按 `Ctrl+T` 打开工具列表启用所需工具，或继续输入让我在不使用工具的情况下回答。"
                )
                assistant_message["content"] = fallback_text
        except Exception:
            pass

        # 向上下文反馈重复调用跳过信息，帮助模型避免重复
        try:
            if locals().get("skipped_duplicates"):
                dup_preview = ", ".join([(d or {}).get("name") or "" for d in (skipped_duplicates or []) if (d or {}).get("name")][:6])
                if dup_preview.strip():
                    messages.append({
                        "role": "user",
                        "synthetic": True,
                        "content": (
                            f"提示：检测到重复的工具调用已被跳过：{dup_preview}。"
                            f"请避免对相同参数重复调用，优先分析原因并调整参数后再试。"
                        ),
                    })
        except Exception:
            pass

        # 限制每轮只执行一个工具调用
        if filtered_tool_calls:
            try:
                filtered_tool_calls = filtered_tool_calls[:1]
                safe_notify(app, "🎯 为提升精准度：本轮仅执行1次工具调用并随后进行思考", severity="success", timeout=3)
            except Exception:
                pass
            assistant_message["tool_calls"] = filtered_tool_calls
            try:
                names = []
                for tc in filtered_tool_calls:
                    fn = (tc or {}).get("function", {})
                    nm = fn.get("name")
                    if nm:
                        names.append(nm)
                if names:
                    safe_notify(app, f"🛠️ 将执行工具: {', '.join(names[:5])}", timeout=3)
            except Exception:
                pass

        # 若需要用户确认/补全，确保追加标记
        try:
            cur = (assistant_message.get("content") or "")
            if requires_user_confirmation(cur) and not has_marker(cur, REQUIRE_USER_MARKERS):
                sep = "\n\n" if not cur.endswith("\n") else "\n"
                assistant_message["content"] = cur + sep + "[STEP_REQUIRE_USER]"
        except Exception:
            pass

        # 附加助手消息
        messages.append(assistant_message)
        try:
            preview = (assistant_message.get("content") or "").strip().replace("\n"," ")[:120]
            names = [((tc or {}).get("function", {}).get("name")) for tc in (assistant_message.get("tool_calls") or [])]
            names = [n for n in names if n][:5]
            logger.debug(f"[iteration] 附加助手消息：content_preview='{preview}', tool_calls={names}")
        except Exception:
            pass

        # 显示助手消息（根据模式）
        try:
            assistant_content = (assistant_message.get("content") or "")
            if assistant_content.strip() and chat_history:
                if streaming:
                    message_added = chat_history.finish_streaming_message(assistant_content)
                    if not message_added:
                        assistant_msg_dict = {"role": "assistant", "content": assistant_content}
                        context_for_assistant = messages[:-1] if messages else []
                        assistant_token_stats = calculate_token_stats(
                            current_message=assistant_msg_dict,
                            context_messages=context_for_assistant,
                        )
                        chat_history.add_message("assistant", assistant_content, token_stats=assistant_token_stats)
                else:
                    assistant_msg_dict = {"role": "assistant", "content": assistant_content}
                    context_for_assistant = messages[:-1] if messages else []
                    assistant_token_stats = calculate_token_stats(
                        current_message=assistant_msg_dict,
                        context_messages=context_for_assistant,
                    )
                    chat_history.add_message("assistant", assistant_content, token_stats=assistant_token_stats)
            # # 规划/确认早停判断
            # try:
            #     if has_marker(assistant_content, PLAN_READY_MARKERS):
            #         context_hint = ""
            #         for idx in range(len(messages) - 2, -1, -1):
            #             if messages[idx].get("role") == "tool":
            #                 ctx = (messages[idx].get("content") or "").strip()
            #                 if ctx:
            #                     context_hint = ctx[:800]
            #                     break
            #         plan_input = assistant_content
            #         if context_hint:
            #             plan_input = f"{assistant_content}\n\n[已识别上下文摘要]\n{context_hint}"
            #         plan = await app._plan_task_steps(plan_input)
            #         steps = (plan.get("steps") or []) if isinstance(plan, dict) else []
            #         if isinstance(plan, dict) and (plan.get("type") == "task") and len(steps) > 1:
            #             plan_text = "\n".join([f"{i+1}. {s}" for i, s in enumerate(steps)])
            #             chat_history.add_message("assistant", f"🧭 已拆分为{len(steps)}个步骤：\n{plan_text}")
            #             await execute_task_steps(app, steps, user_message)
            #             return {"messages": messages, "stop": True}
            # except Exception:
            #     pass
            try:
                if should_pause_for_user(assistant_content):
                    try:
                        logger.debug("[iteration] 早停：等待用户确认/输入")
                    except Exception:
                        pass
                    safe_notify(app, "⏸️ 暂停：等待你的输入或确认后继续。", timeout=4)
                    return {"messages": messages, "stop": True}
            except Exception:
                pass
            # 新增：会话结束或步骤完成早停
            try:
                if should_end_session(assistant_content, has_tool_calls=bool(filtered_tool_calls)):
                    try:
                        logger.debug("[iteration] 早停：会话结束标记命中")
                    except Exception:
                        pass
                    safe_notify(app, "✅ 会话已结束，停止继续迭代。", timeout=4)
                    return {"messages": messages, "stop": True}
            except Exception:
                pass
        except Exception:
            pass

        # 新增：若无工具调用且本轮助手文本与上一轮相同，直接早停，避免重复迭代
        try:
            if (not filtered_tool_calls):
                cur_text = (assistant_message.get("content") or "").strip()
                if cur_text and previous_assistant_text.strip() and (cur_text == previous_assistant_text.strip()):
                    try:
                        logger.debug("[iteration] 早停：连续相同文本且无工具调用")
                    except Exception:
                        pass
                    safe_notify(app, "🛑 检测到重复响应且无工具调用，提前结束。", timeout=5)
                    return {"messages": messages, "stop": True}
        except Exception:
            pass
        # 更新上一轮文本
        try:
            previous_assistant_text = (assistant_message.get("content") or "")
        except Exception:
            previous_assistant_text = previous_assistant_text

        # 执行工具或者结束
        if filtered_tool_calls:
            tool_results = await function_executor.execute_from_tool_calls_async(filtered_tool_calls)
            import json
            for i, tool_result in enumerate(tool_results):
                tool_call = filtered_tool_calls[i]
                func_data = tool_call.get("function", {})
                func_name = func_data.get("name")
                func_args = func_data.get("arguments", "{}")
                if tool_result.get("success"):
                    result_val = tool_result.get("result", "")
                    if isinstance(result_val, Widget):
                        result_str = "(图表可视化结果)"
                        result_obj_for_ui = result_val
                    elif isinstance(result_val, (dict, list)):
                        try:
                            result_str = json.dumps(result_val, ensure_ascii=False)
                        except Exception:
                            result_str = str(result_val)
                        result_obj_for_ui = result_val if isinstance(result_val, dict) else None
                    else:
                        result_str = str(result_val) if result_val is not None else ""
                        result_obj_for_ui = None
                    if not result_str.strip():
                        result_str = "(结果为空)"
                    compressed_text, was_compressed = compress_if_large(result_str, threshold=8000)
                    if chat_history:
                        chat_history.add_tool_call(
                            func_name,
                            func_args,
                            compressed_text if was_compressed else result_str,
                            True,
                            result_obj=result_obj_for_ui,
                        )
                    tool_message = {
                        "role": "tool",
                        "tool_call_id": tool_call.get("id", f"call_{func_name}"),
                        "content": compressed_text if was_compressed else result_str,
                    }
                    messages.append(tool_message)
                    try:
                        safe_notify(app, f"✅ 工具 {func_name} 执行成功", timeout=2)
                    except Exception:
                        pass
                else:
                    error_msg = tool_result.get("error", "执行失败")
                    if not (error_msg or "").strip():
                        error_msg = "(错误信息为空)"
                    if chat_history:
                        chat_history.add_tool_call(func_name, func_args, error_msg, False)
                    tool_message = {
                        "role": "tool",
                        "tool_call_id": tool_call.get("id", f"call_{func_name}"),
                        "content": error_msg or "",
                    }
                    messages.append(tool_message)
                    block_tool_retry_for_current_query = True
                    try:
                        safe_notify(app, f"❌ 工具 {func_name} 执行失败：{error_msg}", severity="warning", timeout=4, markup=False)
                    except Exception:
                        pass
            continue
        else:
            # 仅在流式模式下执行非流式回退尝试，避免重复
            if streaming:
                try:
                    import re
                    provider = getattr(app.ai_client.model_config, "provider", "")
                    current_model = app.ai_client.get_current_model() if hasattr(app.ai_client, "get_current_model") else ""
                    tools_names = []
                    for t in tools:
                        fn = (t or {}).get("function", {})
                        nm = fn.get("name")
                        if nm:
                            tools_names.append(nm)
                    markers = re.findall(r"<\|\s*tool_call_begin\s*\|>(.*?)<\|\s*tool_call_end\s*\|>", getattr(response, "content", "") or "", flags=re.DOTALL)
                    snippet = (getattr(response, "content", "") or "").strip().replace("\n", " ")[:300]
                    last_user = ""
                    for idx in range(len(messages) - 1, -1, -1):
                        if messages[idx].get("role") == "user":
                            last_user = (messages[idx].get("content") or "").strip().replace("\n", " ")[:120]
                            break
                    safe_notify(
                        app,
                        f"🧪 调试：模型未返回结构化工具调用 | 模型: {current_model}/{provider} | 工具数: {len(tools)} | 标记段: {len(markers)}",
                        severity="warning",
                        timeout=5,
                        markup=False,
                    )
                    if tools_names:
                        safe_notify(app, f"🧪 可用工具: {', '.join(tools_names[:6])}", timeout=4, markup=False)
                    if last_user:
                        safe_notify(app, f"🧪 最近用户输入片段: {last_user}", timeout=4, markup=False)
                    if snippet:
                        safe_notify(app, f"🧪 响应片段: {snippet}", timeout=5, markup=False)
                except Exception:
                    pass

                # 新增：非流式一次性回退尝试，尽量拿到结构化工具调用
                try:
                    fallback_resp = await app.ai_client.chat_with_tools_async(messages, tools=tools)
                    fallback_calls = getattr(fallback_resp, "tool_calls", []) or []
                except Exception:
                    fallback_calls = []
                if fallback_calls:
                    filtered_fallback_calls, _ = await filter_and_deduplicate_tool_calls(app, fallback_calls, executed_tool_signatures)
                    if filtered_fallback_calls:
                        safe_notify(app, "🔁 非流式回退获取到工具调用，继续执行", timeout=4)
                        assistant_message["tool_calls"] = filtered_fallback_calls[:1]
                        messages.append(assistant_message)
                        # 显示助手消息（与流式组件对齐）
                        try:
                            assistant_content = (assistant_message.get("content") or "")
                            if assistant_content.strip() and chat_history:
                                message_added = chat_history.finish_streaming_message(assistant_content)
                                if not message_added:
                                    assistant_msg_dict = {"role": "assistant", "content": assistant_content}
                                    context_for_assistant = messages[:-1] if messages else []
                                    assistant_token_stats = calculate_token_stats(
                                        current_message=assistant_msg_dict,
                                        context_messages=context_for_assistant,
                                    )
                                    chat_history.add_message("assistant", assistant_content, token_stats=assistant_token_stats)
                        except Exception:
                            pass
                        # 执行工具并将结果追加到消息
                        try:
                            tool_messages = await process_tool_calls(filtered_fallback_calls[:1], chat_history_widget=chat_history, add_to_base_messages=True)
                            messages.extend(tool_messages or [])
                        except Exception:
                            pass
                        continue
            # 若回退仍未拿到工具调用，则继续下一轮，让模型思考
            safe_notify(app, "⏭️ 未返回结构化工具调用，本轮继续下一轮尝试", timeout=4)
            try:
                logger.debug("[iteration] 本轮未返回结构化tool_calls，继续下一轮")
            except Exception:
                pass
            continue

    if iteration >= max_iterations:
        try:
            logger.debug(f"[iteration] 达到迭代上限：{max_iterations}")
        except Exception:
            pass
        safe_notify(app, f"⚠️ 工具执行次数已达到上限（{max_iterations}），已停止继续。", severity="warning", timeout=5)
        try:
            if chat_history:
                chat_history.add_message(
                    "assistant",
                    (
                        f"工具执行次数已达到上限（{max_iterations}）。"
                        "如需继续，请输入“继续”让我接着执行，"
                        "或按 Ctrl+T 打开工具列表启用/调整所需工具后再试。"
                    ),
                )
        except Exception:
            pass
    return {"messages": messages, "stop": False}


def mentions_next_step(text: str, current_idx: int) -> bool:
    """启发式判断文本是否明确指向“下一步”
    - 命中“下一步”、“接下来”等中文提示
    - 命中“Next”或“next step”等英文提示
    - 明确出现“第{idx+1}步”编号
    """
    try:
        if not text:
            return False
        t = (text or "").lower()
    except Exception:
        t = ""
    if not t.strip():
        return False
    if ("下一步" in t) or ("接下来" in t):
        return True
    try:
        import re
        nxt = current_idx + 1
        if re.search(rf"第\s*{nxt}\s*步", text):
            return True
        if re.search(r"\bnext\b", t) or re.search(r"\bnext\s+step\b", t):
            return True
        if re.search(rf"\bstep\s*{nxt}\b", t):
            return True
    except Exception:
        pass
    return False