"""用户历史输入解析工具

提供将 conversation_history 中的用户历史输入解析为摘要文本的公共方法。
与 chat_flow/ai_helpers 的解析逻辑保持一致，支持中英文冒号。
"""
from typing import List, Dict, Any
import logging
logger = logging.getLogger("ketacli.textual.ai_helpers")



def build_user_history_summary(
    conversation_history: List[Dict[str, Any]] = None,
    limit: int = 10,
    current_task_text: str | None = None,
    exclude_synthetic: bool = True,
) -> str:
    """从会话历史中构造用户历史输入摘要。

    - 仅解析 role=="user" 的消息；
    - 默认跳过合成消息（synthetic==True）；
    - 行级匹配 "用户当前任务：" 或 "用户当前任务:"；
    - 支持全角冒号（：）与半角冒号（:）；
    - 排除与 current_task_text 相同的项（若提供）；
    - 按出现顺序去重，并截断为最近 limit 条；
    - 返回摘要文本：每行以 "- " 前缀；若无则返回 "无"。

    Args:
        conversation_history: 会话历史消息列表
        limit: 限制返回的项目数量
        current_task_text: 当前任务文本（用于排除与其相同的历史项）
        exclude_synthetic: 是否排除合成消息

    Returns:
        str: 摘要文本（带行前缀），若无则为 "无"。
    """
    logger.debug("构建用户历史输入摘要：limit=%s, exclude_synthetic=%s, current_task_text_len=%s",
                 limit, exclude_synthetic, len(current_task_text or ""))
    try:
        ordered_inputs: List[str] = []
        seen = set()
        hist = list(conversation_history or [])
        for _m in hist:
            try:
                if not (isinstance(_m, dict) and (_m.get("role") == "user")):
                    continue
                if exclude_synthetic and _m.get("synthetic") is True:
                    continue
                _c = str(_m.get("content", "")).strip()
                if not _c:
                    continue
                for c in _c.split("\n"):
                    cc = c.strip()
                    if ("用户当前任务：" in cc) or ("用户当前任务:" in cc):
                        if "：" in cc:
                            item = cc.split("：", 1)[-1].strip()
                        elif ":" in cc:
                            item = cc.split(":", 1)[-1].strip()
                        else:
                            item = cc
                        if not item:
                            continue
                        if current_task_text and item == current_task_text:
                            # 排除当前任务本身
                            continue
                        if item in seen:
                            continue
                        seen.add(item)
                        ordered_inputs.append(item)
            except Exception:
                # 单条消息解析失败不影响整体
                pass
        if len(ordered_inputs) > limit:
            ordered_inputs = ordered_inputs[-limit:]
        logger.debug(f"用户历史输入摘要：{ordered_inputs}")
        return "\n".join(f"- {x}" for x in ordered_inputs) if ordered_inputs else "无"
    except Exception:
        return "无"


def build_user_raw_inputs_summary(
    raw_inputs: List[str] | None = None,
    limit: int = 10,
    current_task_text: str | None = None,
) -> str:
    """基于用户原始输入列表构造摘要文本。

    - 输入为用户每次发送的原始文本列表；
    - 去除空行与首尾空白；按出现顺序去重；
    - 若提供 current_task_text，则排除与其完全相同的项；
    - 支持多行输入：按行拆分并逐行处理；
    - 截断为最近 limit 条；
    - 返回每行以 "- " 前缀的摘要文本；若无则返回 "无"。
    """
    try:
        items: List[str] = []
        seen = set()
        for _raw in list(raw_inputs or []):
            try:
                _raw = str(_raw or "").strip()
                if not _raw:
                    continue
                for line in _raw.split("\n"):
                    s = line.strip()
                    if not s:
                        continue
                    if current_task_text and s == current_task_text:
                        continue
                    if s in seen:
                        continue
                    seen.add(s)
                    items.append(s)
            except Exception:
                pass
        if len(items) > limit:
            items = items[-limit:]
        return "\n".join(f"- {x}" for x in items) if items else "无"
    except Exception:
        return "无"