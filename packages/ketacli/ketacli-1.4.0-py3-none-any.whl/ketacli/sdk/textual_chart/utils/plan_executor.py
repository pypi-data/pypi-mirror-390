"""全新计划执行器（PlanExecutor）

目标：提供独立的新执行路径，不与旧逻辑混用。
职责：统一步骤执行、工具调用、早停与状态更新。
"""

from typing import List, Dict, Any, Optional
import logging
from datetime import datetime

from ..widgets import ChatHistoryWidget, ModelSelectorWidget, TaskManagerWidget
from .ai_helpers import get_enabled_tools_openai_format, process_tool_calls, needs_tool_call
from ketacli.sdk.textual_chart.utils.chat_stream import safe_notify

logger = logging.getLogger("ketacli.textual.plan_executor")


# 新版标签常量（不依赖旧文件）
NEW_STEP_NEXT_MARKERS = {"[STEP_NEXT]", "[step_next]"}
NEW_STEP_WAIT_MARKERS = {"[STEP_WAIT]", "[step_wait]"}
NEW_STEP_BLOCKED_MARKERS = {"[STEP_BLOCKED]", "[step_blocked]"}
NEW_TASK_DONE_MARKERS = {"[TASK_DONE]", "[task_done]"}
NEW_STEP_RETRY_MARKERS = {"[STEP_RETRY]", "[step_retry]"}


def _has_marker(text: str, markers: set) -> bool:
    try:
        lower = (text or "").lower()
    except Exception:
        lower = ""
    if not lower:
        return False
    return any((m or "").lower() in lower for m in (markers or set()))


def _normalize_tool_calls(tool_calls: Optional[List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
    """简单去重工具调用：以函数名+参数JSON为签名去重。"""
    res: List[Dict[str, Any]] = []
    seen = set()
    for tc in tool_calls or []:
        fn = (tc or {}).get("function", {})
        name = fn.get("name") or ""
        args = fn.get("arguments") or ""
        sig = f"{name}|{args}"
        if sig in seen:
            continue
        seen.add(sig)
        res.append(tc)
    return res


class PlanExecutor:
    """新的步骤执行器：独立文件中实现，不依赖旧 execute_task_steps。"""

    def __init__(self):
        pass

    async def run(self, app: Any, steps: List[str], original_user_text: str) -> None:
        """执行给定的任务步骤列表。

        - 独立管理状态：`app.plan_status`
        - 统一工具调用：`process_tool_calls`
        - 早停规则：WAIT/BLOCK/DONE 标签
        """
        try:
            setattr(app, "plan_status", "running")
        except Exception:
            pass

        # 组件获取（容错）
        try:
            chat_history = app.query_one("#chat-history", ChatHistoryWidget)
        except Exception:
            chat_history = None
        try:
            model_selector = app.query_one("#model-selector", ModelSelectorWidget)
        except Exception:
            model_selector = None
        try:
            task_manager = app.query_one("#task-manager", TaskManagerWidget)
        except Exception:
            task_manager = None

        # 更新模型（若选择了）
        try:
            selected = model_selector.get_selected_model() if model_selector else None
            if selected:
                app.ai_client = app.ai_client.__class__(
                    system_prompt=getattr(app.ai_client, "system_prompt", ""),
                    model_name=selected,
                )
        except Exception:
            pass

        # 准备基础消息（优先使用应用的现有方法）
        try:
            base_messages = app._prepare_messages(original_user_text)
        except Exception:
            base_messages = [{"role": "user", "content": original_user_text or ""}]

        # 初始化任务管理器
        try:
            if task_manager:
                task_manager.set_tasks(steps)
        except Exception:
            pass

        # 工具定义（新路径：通过 ai_helpers）
        try:
            enabled = getattr(app, "enabled_tools", set()) or set()
            tools = get_enabled_tools_openai_format(enabled)
        except Exception:
            tools = []

        # 初始化会话级记录容器（轻量）
        try:
            if not hasattr(app, "_session_step_records"):
                setattr(app, "_session_step_records", [])
            if not hasattr(app, "_session_tool_records"):
                setattr(app, "_session_tool_records", [])
        except Exception:
            pass

        # 步骤执行
        for idx, step_text in enumerate(steps):
            # 记录：步骤开始
            logger.info(f"[recv][step] 第 {idx+1} 步开始: {step_text}")

            step_record: Dict[str, Any] = {
                "index": idx + 1,
                "text": step_text,
                "iteration": 0,
                "status": "in_progress",
                "start_ts": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
            try:
                if chat_history:
                    chat_history.add_message("assistant", f"🔸 正在执行第 {idx+1} 步：{step_text}")
            except Exception:
                pass
            try:
                if task_manager:
                    task_manager.update_status(idx + 1, "in_progress", 0)
            except Exception:
                pass

            # 将当前步骤加入上下文并请求模型（允许自动工具）
            user_turn = {"role": "user", "content": step_text}
            messages = list(base_messages) + [user_turn]
            max_iterations = 8
            iteration = 0

            while iteration < max_iterations:
                iteration += 1
                step_record["iteration"] = iteration
                try:
                    if task_manager:
                        task_manager.update_status(idx + 1, "in_progress", iteration)
                except Exception:
                    pass

                # 若当前文本表征为不需要工具，仍然正常聊天；否则提示工具执行
                tool_choice = "auto"
                try:
                    if not needs_tool_call(step_text):
                        tool_choice = None
                except Exception:
                    tool_choice = "auto"

                try:
                    resp = await app.ai_client.chat_with_tools_async(
                        messages,
                        tools=tools,
                        tool_choice=tool_choice,
                    )
                except Exception as e:
                    safe_notify(app, f"模型调用异常：{e}", severity="error", timeout=4)
                    logger.warning(f"[state] 第 {idx+1} 步模型调用异常: {e}")
                    logger.info(f"步骤执行结束（第 {idx+1} 步，第 {iteration} 次迭代）")
                    break

                assistant_text = getattr(resp, "content", "") or ""
                tool_calls = _normalize_tool_calls(getattr(resp, "tool_calls", None))
                if tool_calls:
                    try:
                        for tc in tool_calls:
                            fn = (tc or {}).get("function", {})
                            name = fn.get("name") or ""
                            args = fn.get("arguments") or ""
                            logger.info(f"[tool] 第 {idx+1} 步调用: {name} (args_len={len(str(args))})")
                            # 记录工具调用（轻量摘要）
                            getattr(app, "_session_tool_records", []).append({
                                "step_index": idx + 1,
                                "name": name,
                                "args_preview": (str(args)[:200] if args else ""),
                                "ts": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            })
                    except Exception:
                        pass

                # 展示助手消息
                try:
                    if chat_history:
                        chat_history.add_message("assistant", assistant_text)
                except Exception:
                    pass

                # 早停与暂停判定（新标签）——仅当最后一步才允许 COMPLETE/DONE 直接结束
                is_final_step = (idx == len(steps) - 1)
                if _has_marker(assistant_text, NEW_TASK_DONE_MARKERS):
                    if is_final_step:
                        setattr(app, "plan_status", "completed")
                        try:
                            if task_manager:
                                task_manager.update_status(idx + 1, "completed", iteration)
                        except Exception:
                            pass
                        safe_notify(app, "✅ 任务已完成", timeout=3)
                        step_record["status"] = "completed"
                        step_record["transition_reason"] = "助手标记任务完成"
                        logger.info(f"[state] 会话状态=completed")
                        logger.info(f"步骤执行结束（第 {idx+1} 步，第 {iteration} 次迭代）")
                        try:
                            getattr(app, "_session_step_records", []).append(step_record)
                        except Exception:
                            pass
                        break
                    else:
                        try:
                            if task_manager:
                                task_manager.update_status(idx + 1, "completed", iteration)
                        except Exception:
                            pass
                        step_record["status"] = "completed"
                        step_record["transition_reason"] = "非最后一步助手标记完成，推进下一步"
                        logger.info(f"[transition] 第 {idx+1} 步 → NEXT (助手标记)")
                        logger.info(f"[state] 会话状态=running")
                        logger.info(f"步骤执行结束（第 {idx+1} 步，第 {iteration} 次迭代）")
                        try:
                            getattr(app, "_session_step_records", []).append(step_record)
                        except Exception:
                            pass
                        break
                if _has_marker(assistant_text, NEW_STEP_BLOCKED_MARKERS):
                    setattr(app, "plan_status", "paused")
                    safe_notify(app, "⛔ 当前步骤受阻，已暂停", severity="warning", timeout=4)
                    try:
                        if task_manager:
                            task_manager.update_status(idx + 1, "blocked", iteration)
                    except Exception:
                        pass
                    step_record["status"] = "blocked"
                    step_record["transition_reason"] = "助手标记受阻"
                    logger.info(f"[transition] 第 {idx+1} 步 → BLOCK")
                    logger.info(f"[state] 会话状态=paused")
                    logger.info(f"步骤执行结束（第 {idx+1} 步，第 {iteration} 次迭代）")
                    try:
                        getattr(app, "_session_step_records", []).append(step_record)
                    except Exception:
                        pass
                    return
                if _has_marker(assistant_text, NEW_STEP_WAIT_MARKERS):
                    setattr(app, "plan_status", "paused")
                    safe_notify(app, "⏸ 当前步骤需要你的确认或补充信息", severity="warning", timeout=4)
                    try:
                        if task_manager:
                            task_manager.update_status(idx + 1, "paused", iteration)
                    except Exception:
                        pass
                    step_record["status"] = "paused"
                    step_record["transition_reason"] = "助手标记需要用户确认/信息"
                    logger.info(f"[transition] 第 {idx+1} 步 → PAUSE")
                    logger.info(f"[state] 会话状态=paused")
                    logger.info(f"步骤执行结束（第 {idx+1} 步，第 {iteration} 次迭代）")
                    try:
                        getattr(app, "_session_step_records", []).append(step_record)
                    except Exception:
                        pass
                    return

                # RETRY 标签：继续迭代，达到上限则暂停
                if _has_marker(assistant_text, NEW_STEP_RETRY_MARKERS):
                    logger.info(f"[transition] 第 {idx+1} 步 → RETRY (迭代 {iteration}/{max_iterations})")
                    base_messages.append({"role": "assistant", "content": assistant_text})
                    if iteration >= max_iterations:
                        setattr(app, "plan_status", "paused")
                        try:
                            if task_manager:
                                task_manager.update_status(idx + 1, "paused", iteration)
                        except Exception:
                            pass
                        safe_notify(app, "⏸ 达到迭代上限，仍需重试，已暂停", severity="warning", timeout=4)
                        step_record["status"] = "paused"
                        step_record["transition_reason"] = "达到迭代上限，仍需重试"
                        logger.info(f"[state] 会话状态=paused")
                        logger.info(f"步骤执行结束（第 {idx+1} 步，第 {iteration} 次迭代）")
                        try:
                            getattr(app, "_session_step_records", []).append(step_record)
                        except Exception:
                            pass
                        return
                    messages = list(base_messages) + [user_turn]
                    continue

                # 补充assistant消息中的工具调用以满足OpenAI工具序（如果存在）
                if tool_calls:
                    try:
                        base_messages.append({
                            "role": "assistant",
                            "content": assistant_text,
                            "tool_calls": tool_calls,
                        })
                    except Exception:
                        base_messages.append({"role": "assistant", "content": assistant_text})
                else:
                    base_messages.append({"role": "assistant", "content": assistant_text})

                # 执行工具并将结果加入上下文
                if tool_calls:
                    try:
                        tool_messages = await process_tool_calls(
                            tool_calls,
                            chat_history_widget=chat_history,
                            add_to_base_messages=True,
                        )
                        base_messages.extend(tool_messages or [])
                        logger.info(f"[tool] 第 {idx+1} 步工具结果消息数: {len(tool_messages or [])}")
                    except Exception as e:
                        safe_notify(app, f"工具调用异常：{e}", severity="warning", timeout=4)
                        logger.warning(f"[tool] 第 {idx+1} 步工具调用异常: {e}")

                # 总结与转移决定（阶段 4）
                try:
                    decision = await self._summarize_and_decide(app, base_messages, assistant_text)
                    tag = (decision.get("tag") or "").upper()
                    step_record["summary_tag"] = tag
                    logger.info(f"[summary] 第 {idx+1} 步判定标签: {tag}")
                except Exception:
                    tag = "NEXT"
                    step_record["summary_tag"] = tag

                if tag == "RETRY":
                    logger.info(f"[transition] 第 {idx+1} 步 → RETRY (总结判定，迭代 {iteration}/{max_iterations})")
                    if iteration >= max_iterations:
                        setattr(app, "plan_status", "paused")
                        try:
                            if task_manager:
                                task_manager.update_status(idx + 1, "paused", iteration)
                        except Exception:
                            pass
                        safe_notify(app, "⏸ 达到迭代上限，仍需重试，已暂停", severity="warning", timeout=4)
                        step_record["status"] = "paused"
                        step_record["transition_reason"] = "达到迭代上限，仍需重试（总结判定）"
                        logger.info(f"[state] 会话状态=paused")
                        logger.info(f"步骤执行结束（第 {idx+1} 步，第 {iteration} 次迭代）")
                        try:
                            getattr(app, "_session_step_records", []).append(step_record)
                        except Exception:
                            pass
                        return
                    messages = list(base_messages) + [user_turn]
                    continue

                if tag in ("PAUSE", "WAIT"):
                    setattr(app, "plan_status", "paused")
                    try:
                        if task_manager:
                            task_manager.update_status(idx + 1, "paused", iteration)
                    except Exception:
                        pass
                    safe_notify(app, "⏸ 总结判定需要你的确认或补充信息", severity="warning", timeout=4)
                    step_record["status"] = "paused"
                    step_record["transition_reason"] = "需要用户确认或补充信息"
                    logger.info(f"[transition] 第 {idx+1} 步 → PAUSE")
                    logger.info(f"[state] 会话状态=paused")
                    logger.info(f"步骤执行结束（第 {idx+1} 步，第 {iteration} 次迭代）")
                    try:
                        getattr(app, "_session_step_records", []).append(step_record)
                    except Exception:
                        pass
                    return
                if tag in ("BLOCK", "BLOCKED"):
                    setattr(app, "plan_status", "paused")
                    try:
                        if task_manager:
                            task_manager.update_status(idx + 1, "blocked", iteration)
                    except Exception:
                        pass
                    safe_notify(app, "🛑 总结判定当前步骤被阻塞", severity="warning", timeout=4)
                    step_record["status"] = "blocked"
                    step_record["transition_reason"] = "外部资源/权限受限或错误阻塞"
                    logger.info(f"[transition] 第 {idx+1} 步 → BLOCK")
                    logger.info(f"[state] 会话状态=paused")
                    logger.info(f"步骤执行结束（第 {idx+1} 步，第 {iteration} 次迭代）")
                    try:
                        getattr(app, "_session_step_records", []).append(step_record)
                    except Exception:
                        pass
                    return
                if tag in ("COMPLETE", "DONE"):
                    if is_final_step:
                        setattr(app, "plan_status", "completed")
                        try:
                            if task_manager:
                                task_manager.update_status(idx + 1, "completed", iteration)
                        except Exception:
                            pass
                        safe_notify(app, "✅ 任务已完成（总结判定）", timeout=3)
                        step_record["status"] = "completed"
                        step_record["transition_reason"] = "总结判定完成"
                        logger.info(f"[transition] 第 {idx+1} 步 → COMPLETE")
                        logger.info(f"[state] 会话状态=completed")
                        logger.info(f"步骤执行结束（第 {idx+1} 步，第 {iteration} 次迭代）")
                        try:
                            getattr(app, "_session_step_records", []).append(step_record)
                        except Exception:
                            pass
                        break
                    else:
                        try:
                            if task_manager:
                                task_manager.update_status(idx + 1, "completed", iteration)
                        except Exception:
                            pass
                        step_record["status"] = "completed"
                        step_record["transition_reason"] = "非最后一步按NEXT推进"
                        logger.info(f"[transition] 第 {idx+1} 步 → NEXT (非最后一步)")
                        logger.info(f"[state] 会话状态=running")
                        logger.info(f"步骤执行结束（第 {idx+1} 步，第 {iteration} 次迭代）")
                        try:
                            getattr(app, "_session_step_records", []).append(step_record)
                        except Exception:
                            pass
                        break

                # 默认推进到下一步
                try:
                    if task_manager:
                        task_manager.update_status(idx + 1, "completed", iteration)
                except Exception:
                    pass
                step_record["status"] = "completed"
                step_record["transition_reason"] = "默认推进到下一步"
                logger.info(f"[transition] 第 {idx+1} 步 → NEXT")
                logger.info(f"[state] 会话状态=running")
                logger.info(f"步骤执行结束（第 {idx+1} 步，第 {iteration} 次迭代）")
                try:
                    getattr(app, "_session_step_records", []).append(step_record)
                except Exception:
                    pass
                break

        # 所有步骤结束后，若未显式置为完成，则置为完成
        try:
            if getattr(app, "plan_status", "running") != "paused":
                setattr(app, "plan_status", "completed")
                if chat_history:
                    chat_history.add_message("assistant", "✅ 任务步骤执行完成")
                logger.info("[state] 会话状态=completed")
        except Exception:
            pass

        # 执行完毕尝试保存会话（含步骤与工具记录）
        try:
            if hasattr(app, "_save_current_session"):
                app._save_current_session()
        except Exception:
            pass

    async def _summarize_and_decide(self, app: Any, messages: List[Dict[str, Any]], assistant_text: str) -> Dict[str, Any]:
        """对当前步骤进行总结并给出转移决定。

        返回格式示例：{"tag": "NEXT"}；可取值：NEXT、PAUSE、BLOCK、COMPLETE、DONE、WAIT、BLOCKED、RETRY。
        """

        prompt = """你是一个严格的步骤执行总结器。
- 仅基于最近的上下文消息（assistant 与 tool），并结合“当前步骤的目标”进行判定；不要参考更早的对话。
- 最近消息选择：以最近一条非空的工具或助手消息为主，若两者同时存在则共同参考。
- 判定分场景：
  1) 文档/语法/规则检索类步骤（例如：检索 SPL 语法/规则、调用 get_docs、最近的工具/助手内容呈现文档结构：以标题开头、包含“核心原则/黄金模板/常见错误与修正/生成检查清单”等段落）：
     - 只要返回了非空且连贯的文档内容，并且未出现“错误/异常/未找到/空结果/黄色提示（如 [yellow] 或‘结果为空’）”，则判定为 NEXT。
     - 不要因为文档中出现“错误写法/错误示例/修正建议”等说明性内容而判定 RETRY（这些属于文档说明，并非工具执行失败）。
  2) 数据查询/执行类步骤（例如：检索日志/指标数据、执行统计/绘图等）：
     - 若最近消息明确出现“错误/异常/语法错误/修复建议/空结果/未查询到数据/提示放宽条件/黄色提示（如 [yellow] 或‘结果为空’）”，则返回 RETRY。下一轮应调整参数，避免与上一次完全相同（例如扩大时间范围、改用模糊匹配、减少过滤、必要时移除过严的 origin 过滤）。
     - 若无上述失败或空结果信号，则返回 NEXT。
- 标签使用：
  - 若任务整体完成，返回 COMPLETE（仅在最后一步使用）。
  - 若本步骤需要暂停，返回 PAUSE。
  - 若本步骤被阻塞，返回 BLOCKED。
  - 若本步骤已完成，返回 NEXT。
  - 若需要重试，返回 RETRY。
- 仅输出一个 JSON：{"tag": "NEXT|PAUSE|BLOCK|COMPLETE|RETRY"}。
- 不要添加解释或额外字段。"""

        recent = messages[-20:] if messages and len(messages) > 20 else list(messages or [])
        msgs = recent + [
            {"role": "system", "content": prompt},
            {"role": "assistant", "content": assistant_text or ""},
        ]
        try:
            logger.info(f"[prompt] 执行总结器提示：{msgs}")
            resp = await app.ai_client.chat_async(msgs)
            logger.info(f"[response] 执行总结器响应：{resp}")
            text = getattr(resp, "content", "") or ""
            import json as _json
            obj = _json.loads(text)
            if not isinstance(obj, dict):
                raise ValueError("响应不是对象")
            return obj
        except Exception:
            return {"tag": "NEXT"}