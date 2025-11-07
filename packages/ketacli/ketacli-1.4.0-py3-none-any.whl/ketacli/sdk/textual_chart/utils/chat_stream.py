import asyncio
import logging
from types import SimpleNamespace
from typing import Any, List, Tuple

logger = logging.getLogger("ketacli.textual")


def safe_notify(app, message: str, severity: str = None, timeout: int = None, **kwargs) -> None:
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


async def stream_chat_with_tools_async(app: Any, messages: List[dict], tools: List[dict]):
    """异步流式聊天（支持工具调用）：实时推送chunk，避免等待全部完成。

    使用异步队列实现流式聊天功能，将AI响应实时推送给用户界面，
    无论是普通文本还是工具调用结果，都通过流式方式返回。
    """
    loop = asyncio.get_running_loop()
    queue: asyncio.Queue = asyncio.Queue()
    done = asyncio.Event()

    # 启动前记录一些上下文信息
    try:
        provider = getattr(app.ai_client.model_config, "provider", "")
        current_model = app.ai_client.get_current_model() if hasattr(app.ai_client, "get_current_model") else ""
        logger.debug(f"[stream_tools] 启动: provider={provider}, model={current_model}, messages_len={len(messages) if isinstance(messages, list) else 1}")
    except Exception:
        pass

    # 新增：启动调试通知
    safe_notify(app, "🔄 启动流式工具请求", timeout=2)

    def producer():
        try:
            for chunk in app.ai_client.stream_chat(messages, tools=tools, tool_choice="auto"):
                # 解析chunk，转换为统一格式
                if isinstance(chunk, str):
                    processed_chunk = {"content": chunk}
                elif isinstance(chunk, dict):
                    processed_chunk = chunk
                else:
                    try:
                        processed_chunk = {"content": str(chunk)}
                    except Exception:
                        processed_chunk = {"content": "无法解析的内容"}
                asyncio.run_coroutine_threadsafe(queue.put(processed_chunk), loop)
        except Exception as e:
            logger.error(f"[stream_tools] 生产者异常: {type(e).__name__}: {e}")
            asyncio.run_coroutine_threadsafe(queue.put({"content": f"\n[流式错误] {e}"}), loop)
        finally:
            asyncio.run_coroutine_threadsafe(done.set(), loop)

    # 启动生产者线程
    import threading
    threading.Thread(target=producer, daemon=True).start()

    # 新增：统计收到的片段数量
    received_chunks = 0

    # 消费者：异步获取队列中的chunk并处理
    while not done.is_set() or not queue.empty():
        try:
            chunk = await asyncio.wait_for(queue.get(), timeout=0.1)
            received_chunks += 1
            yield chunk
        except asyncio.TimeoutError:
            continue
        except Exception as e:
            logger.error(f"[stream_tools] 消费者异常: {type(e).__name__}: {e}")
            yield {"content": f"\n[流式处理错误] {e}"}
            break

    # 新增：结束调试通知
    safe_notify(app, f"📤 流式结束：收到 {received_chunks} 个片段", timeout=3)
    if received_chunks == 0:
        safe_notify(app, "⚠️ 流式接口未返回任何数据（内容/工具调用均为空）", severity="warning", timeout=5)


async def stream_chat_async(app: Any, messages: List[dict]):
    """异步流式聊天：实时推送chunk，避免等待全部完成。"""
    loop = asyncio.get_running_loop()
    queue: asyncio.Queue = asyncio.Queue()
    done = asyncio.Event()
    yield_count = 0

    # 启动前记录一些上下文信息
    try:
        provider = getattr(app.ai_client.model_config, "provider", "")
        current_model = app.ai_client.get_current_model() if hasattr(app.ai_client, "get_current_model") else ""
        logger.debug(f"[stream] 启动: provider={provider}, model={current_model}, messages_len={len(messages) if isinstance(messages, list) else 1}")
    except Exception:
        pass

    def producer():
        try:
            for chunk in app.ai_client.stream_chat(messages):
                asyncio.run_coroutine_threadsafe(queue.put(chunk), loop)
        except Exception as e:
            logger.error(f"[stream] 生产者异常: {type(e).__name__}: {e}")
            asyncio.run_coroutine_threadsafe(queue.put(f"\n[流式错误] {e}"), loop)
        finally:
            loop.call_soon_threadsafe(done.set)

    # 在线程中运行同步的流式生成器
    producer_task = asyncio.create_task(asyncio.to_thread(producer))

    try:
        while True:
            if done.is_set() and queue.empty():
                break
            try:
                chunk = await asyncio.wait_for(queue.get(), timeout=0.5)
                yield_count += 1
                yield chunk
            except asyncio.TimeoutError:
                if done.is_set():
                    break
    finally:
        logger.debug(f"[stream] 结束: yielded={yield_count}, done={done.is_set()}, queue_empty={queue.empty()}")
        await producer_task


async def stream_and_process_response(app: Any, messages: List[dict], tools: List[dict], streaming_widget) -> Tuple[SimpleNamespace, List[dict]]:
    """流式获取并处理AI响应，返回响应对象和过滤后的工具调用列表。"""
    accumulated_content = ""
    tool_calls_buffer: List[dict] = []
    is_tool_call = False

    # 新增：开始调试通知
    safe_notify(app, "⏳ 正在流式获取模型响应...", timeout=2)

    # 启动流式处理
    async for chunk in stream_chat_with_tools_async(app, messages, tools):
        # 文本内容
        if "content" in chunk and chunk.get("content"):
            content = chunk.get("content", "")
            accumulated_content += content
            try:
                streaming_widget.append_content(content)
            except Exception:
                pass

        # 工具调用
        if "tool_calls" in chunk and chunk.get("tool_calls"):
            is_tool_call = True
            for tool_call in chunk.get("tool_calls", []):
                if tool_call not in tool_calls_buffer:
                    tool_calls_buffer.append(tool_call)
            try:
                streaming_widget.append_content("正在处理工具调用...\n")
            except Exception:
                pass

    # 构造响应对象
    response = SimpleNamespace()
    response.content = accumulated_content
    response.tool_calls = tool_calls_buffer if is_tool_call else []

    # 新增：若流式未返回结构化tool_calls，但文本中包含标记，则回退解析
    try:
        if (not response.tool_calls) and (response.content or "").strip():
            parsed = app.ai_client._parse_tool_calls_from_text(response.content)
            if parsed:
                response.tool_calls = parsed
                is_tool_call = True
    except Exception:
        pass

    try:
        content_len = len(response.content or "")
        enabled_attr = getattr(app, "enabled_tools", None)
        if isinstance(enabled_attr, dict):
            enabled_names = set(enabled_attr.keys())
        elif isinstance(enabled_attr, (set, list, tuple)):
            enabled_names = set(enabled_attr)
        else:
            enabled_names = set()
        filtered_tool_calls = [
            tc for tc in (response.tool_calls or [])
            if ((tc or {}).get("function", {}).get("name") in enabled_names)
        ]
        tc_len = len(filtered_tool_calls)
        # 新增：禁用过滤统计与空响应提醒
        unfiltered_len = len(response.tool_calls or [])
        disabled_count = max(unfiltered_len - tc_len, 0)
        safe_notify(app, f"📩 收到响应：内容长度 {content_len}，解析到工具调用 {tc_len} 个（已按启用工具过滤）", timeout=3)
        if disabled_count > 0:
            safe_notify(app, f"🧩 模型提供 {unfiltered_len} 次工具调用，其中 {disabled_count} 次被禁用过滤", timeout=4)
        if content_len == 0 and tc_len == 0:
            safe_notify(app, "⚠️ 模型未返回文本或工具调用，按空响应处理", severity="warning", timeout=5)
    except Exception:
        filtered_tool_calls = response.tool_calls or []

    logger.debug(f"[stream] 完成流式响应：content_len={len(response.content or '')}，tool_calls={len(filtered_tool_calls or [])}")
    return response, filtered_tool_calls


def augment_system_prompt(base: str) -> str:
    """将系统级工具调用规则注入到基础提示词中，避免重复追加。

    幂等策略：若基础提示词已包含规则锚点（首行或关键行），则不再二次追加。
    """
    rules = (
        "你是一个可靠的助手，工具调用策略为自动模式。\n"
        "当你决定调用工具时，请遵循以下规则：\n"
        "1) 每轮至多调用一个工具；调用后必须基于工具结果进行分析并输出明确文本结论。\n"
        "2) 避免连续多次重复调用同一工具或在已具备足够信息时再次调用。\n"
        "3) 如工具调用失败，请解释原因并给出替代方案或推断结论。\n"
        "4) 仅在明确缺少信息且无法产出结论时，才再次考虑调用工具。\n"
        "5) 不要返回只有工具调用而没有任何文本内容的响应。\n"
        "6) 若任务涉及未明确枚举的复数对象（如‘各个服务/每台主机’），先进行信息发现并枚举对象。\n"
        "7) 对于查询/检索/日志类任务，必须使用提供的工具完成检索，禁止编造或模拟数据结果。\n"
        "8) 若工具返回空结果、出现‘未查询到数据/未找到’或黄色提示（例如提示放宽条件），必须修改参数后重试，\n"
        "   不得复用与上一轮完全相同的参数。优先策略：扩大时间范围（如 -2h/-6h）、将精确匹配改为 like/contains、\n"
        "   减少 where 过滤、必要时移除过严的 origin 过滤。每次重试必须在文本末标注 [STEP_RETRY]，并简要说明参数与上一轮的差异。\n"
        "9) 连续两次重试仍为空时，应停止重试，给出原因分析与后续建议（例如字段不存在、数据落库延迟、仓库选择不当等）。\n"
    )
    try:
        base_str = base or ""
    except Exception:
        base_str = ""
    anchor1 = "你是一个可靠的助手，工具调用策略为自动模式。"
    anchor2 = "当你决定调用工具时，请遵循以下规则："
    if (anchor1 in base_str) or (anchor2 in base_str):
        # 已包含规则锚点，避免重复追加
        return base_str
    return f"{base_str}\n\n{rules}".strip()


def sanitize_tool_messages(messages: list, provider: str) -> list:
    try:
        prov = (provider or "").lower()
    except Exception:
        prov = ""
    if "openai" not in prov:
        return messages
    sanitized = []
    allowed_ids = set()
    for msg in messages:
        role = msg.get("role")
        if role == "assistant":
            tool_calls = msg.get("tool_calls") or []
            allowed_ids = set([
                tc.get("id") for tc in tool_calls if isinstance(tc, dict)
            ])
            sanitized.append(msg)
        elif role == "tool":
            tool_id = msg.get("tool_call_id")
            if tool_id and tool_id in allowed_ids:
                sanitized.append(msg)
        else:
            allowed_ids = set()
            sanitized.append(msg)
    return sanitized


def enforce_openai_tool_sequence(msgs: list) -> tuple[list, int, int]:
    sanitized = []
    removed_assistant = 0
    removed_tool = 0
    i = 0
    n = len(msgs)
    while i < n:
        msg = msgs[i]
        role = msg.get("role")
        if role != "assistant":
            if role == "tool":
                removed_tool += 1
            else:
                sanitized.append(msg)
            i += 1
            continue
        tool_calls = msg.get("tool_calls") or []
        if not tool_calls:
            sanitized.append(msg)
            i += 1
            continue
        ids = [tc.get("id") for tc in tool_calls if isinstance(tc, dict) and tc.get("id")]
        j = i + 1
        matched_ids = []
        collected_tools = []
        while j < n and msgs[j].get("role") == "tool":
            tcid = msgs[j].get("tool_call_id")
            if tcid in ids:
                matched_ids.append(tcid)
                collected_tools.append(msgs[j])
            j += 1
        if set(matched_ids) == set(ids):
            sanitized.append(msg)
            sanitized.extend(collected_tools)
            i = j
        else:
            removed_assistant += 1
            i = j
    return sanitized, removed_assistant, removed_tool


async def process_tool_sequence(app, messages: list) -> tuple:
    try:
        msgs, ra, rt = enforce_openai_tool_sequence(messages)
        if ra or rt:
            safe_notify(
                app,
                f"🧩 请求前已规范化：移除不完整assistant {ra} 条/孤立tool {rt} 条",
                severity="warning",
                timeout=3
            )
        last_assistant_idx = None
        for idx in range(len(msgs)-1, -1, -1):
            if msgs[idx].get("role") == "assistant":
                last_assistant_idx = idx
                break
        if last_assistant_idx is not None:
            ids = [tc.get("id") for tc in msgs[last_assistant_idx].get("tool_calls") or [] if isinstance(tc, dict) and tc.get("id")]
            j = last_assistant_idx + 1
            following = 0
            while j < len(msgs) and msgs[j].get("role") == "tool":
                following += 1
                j += 1
            if ids:
                safe_notify(app, f"🔗 最近assistant工具调用: {len(ids)}，后续tool消息: {following}", timeout=3)
        return msgs, ra, rt
    except Exception:
        safe_notify(app, "🔧 解析最近assistant工具调用失败", severity="warning", timeout=3)
        return messages, 0, 0