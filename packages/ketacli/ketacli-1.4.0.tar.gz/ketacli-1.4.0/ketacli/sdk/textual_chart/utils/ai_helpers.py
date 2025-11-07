"""AI处理和工具调用相关的辅助函数

此模块提供了与AI处理和工具调用相关的辅助函数，用于支持交互式聊天应用。
"""

import asyncio
import json
import re
import logging
from typing import List, Dict, Any, Optional, Union, Tuple

from ketacli.sdk.ai.client import AIClient
from ketacli.sdk.ai.function_call import function_registry, function_executor
from ketacli.sdk.ai.tool_output_compressor import compress_if_large
from textual.widget import Widget

from ketacli.sdk.textual_chart.utils.chat_stream import safe_notify
from ketacli.sdk.textual_chart.utils.history_utils import build_user_history_summary, build_user_raw_inputs_summary

# 设置日志记录器
logger = logging.getLogger("ketacli.textual.ai_helpers")

async def assess_planning_readiness(ai_client: AIClient, user_text: str) -> dict:
    """评估是否应立即生成计划，或先进行信息发现。
    
    分析用户输入文本，判断是否有足够信息直接生成执行计划，或需要先进行信息收集。
    使用AI模型进行判断，失败时回退到基于关键词的启发式判断。
    
    Args:
        ai_client: AI客户端实例
        user_text: 用户输入的文本
        
    Returns:
        dict: 包含plan_now(是否立即规划)和reason(原因)的字典
    """
    try:
        prompt = (
            "你是任务规划时机判断助手。\n"
            "判断当前用户需求是否需要先进行信息发现（例如列出服务/实体）再生成详细计划。\n"
            "若当前信息不足以明确拆分任务，请返回 plan_now=false。\n"
            "仅输出JSON且不含Markdown代码块，格式："
            "{\"plan_now\": true|false, \"reason\": \"string\"}。\n"
            "判断标准举例：包含'每个/各个/所有/逐个/分别'且未枚举对象时，多为先发现。\n"
        )
        messages = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": user_text},
        ]
        resp = await ai_client.chat_async(messages, temperature=0.0)
        raw = (resp.content or "").strip()
        data = json.loads(raw)
        plan_now = bool(data.get("plan_now"))
        reason = str(data.get("reason") or "")
        return {"plan_now": plan_now, "reason": reason}
    except Exception:
        # 启发式回退：检测典型词汇与未明确枚举
        text = (user_text or "").strip()
        lowered = text.lower()
        hints = ["各个", "每个", "所有", "逐个", "分别", "每台", "每项", "每个服务", "各服务"]
        has_plural_hint = any(h in text for h in hints)
        # 简单枚举检测：是否出现多个逗号分隔项
        enumerated = bool(re.search(r"[，,]\s*\S+[，,]", text))
        plan_now = not has_plural_hint or enumerated
        reason = "启发式判断：{}".format("已枚举或无复数提示" if plan_now else "疑似需要先列出实体")
        return {"plan_now": plan_now, "reason": reason}

# 从Markdown文件读取前置步骤，每行一个步骤
def _load_md_steps(fname: str) -> List[str]:
    try:
        from pathlib import Path
        p = Path(__file__).resolve().parents[2] / "ai" / "prompts" / fname
        text = p.read_text(encoding="utf-8")
        lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
        normalized: List[str] = []
        for ln in lines:
            ln = re.sub(r"^\s*[\-\*\u2022]+\s*", "", ln)  # 项目符号
            ln = re.sub(r"^\s*\d+[\.\)]\s*", "", ln)     # 编号
            if ln:
                normalized.append(ln)
        return normalized
    except Exception as e:
        logger.warning(f"读取步骤文件失败：{fname}：{e}")
        return []

async def plan_task_steps(ai_client: AIClient, user_text: str, enabled_tools: set = None, conversation_history: List[Dict] = None, user_raw_inputs: List[str] = None, skills_context: List[Dict] = None) -> dict:
    """使用AI判断类型与复杂度，并生成步骤或直接回答。
    
    根据用户输入的文本，使用AI模型先判断类型（问题/任务），并在为任务时按复杂度拆分为可执行的步骤列表。
    问题类型不拆分，交由上游直接回答。
    
    Args:
        ai_client: AI客户端实例
        user_text: 用户输入的文本
        enabled_tools: 已启用的工具集合
        conversation_history: 会话历史，用于上下文摘要
        
    Returns:
        dict: {"type": "question|task", "complexity": "low|high", "steps": [str]}
    """
    logger.debug("使用AI判断复杂度并生成任务步骤列表")
    try:
        prompt = """你是任务规划助手，需先精准判断用户输入类型为问题类或任务类，核心区分及规则如下：
1. 类型判断：仅当用户需求是“执行特定操作以获取结果”时判定为task类；仅当用户需求是“询问信息、确认身份、表达问候”等无需操作执行的场景时判定为question类。
2. 步骤拆分：仅task类需按复杂度（low：3-5步可完成；high：5步以上）拆分步骤，步骤需简洁、可执行，不包含编号，仅保留文字本身；question类steps为空数组或省略。
3. 历史关联：拆分task步骤时必须关注用户历史消息，确保步骤完全匹配用户当前及历史累计需求，避免遗漏关键条件（如特定仓库名称）。
4. 不要自行编造技能描述，必须根据上下文自动生成；例如：不要自行生成SPL语句。
5. 技能描述中包含"[重要]"等提示的，必须带上该步骤，不能省略。
6. 严禁在steps中出现SPL/SQL/Shell命令或工具调用参数示例；不要输出任何查询语句、命令、代码片段或被反引号包裹的内容。
7. 即使技能上下文中包含示例或语法，也不要把这些示例放入steps；steps只保留自然语言动作描述，例如“使用工具 get_docs 查询语法说明”，不要包含参数或查询内容。
8. steps中的每个字符串不得包含形似查询语句的内容（例如包含 index=、search2、管道符"|"等）。如需构建查询，由后续执行器负责，steps中不写出具体查询。
严格按格式输出JSON，不包含多余文字，不使用Markdown代码块，格式为：
{\"type\": \"question|task\", \"complexity\": \"low|high\", \"steps\": [\"步骤文本\"]}
"""

        # 使用通用转换方法将原始文本转为预期格式
        expected_format = (
            "{\n"
            "  \"type\": \"question|task\",\n"
            "  \"complexity\": \"low|high\",\n"
            "  \"steps\": [\"步骤文本\"]\n"
            "}"
        )
        parsed = await convert_to_expected_format(
            ai_client=ai_client,
            raw_text=user_text,
            system_prompt=prompt,
            expected_format=expected_format,
            conversation_history=conversation_history,
            raw_inputs=user_raw_inputs,
            skills_context=skills_context,
        )
        logger.debug(f"任务规划原始回复：{parsed}")


        steps: List[str] = []
        _type: str = "task"
        task_type: str = "other"
        complexity: str = "low"
        
        _type_raw = str(parsed.get("type") or "").strip().lower()
        is_question = _type_raw in ("question", "问题", "问题类", "qa")
        _type = "question" if is_question else "task"
        task_type = str(parsed.get("task_type") or "").strip().lower() or "other"
        complexity = str(parsed.get("complexity") or "").strip().lower() or "low"
        if is_question:
            steps = []
            return {"type": _type, "complexity": complexity, "steps": steps, "task_type": task_type}
        else:
            steps = parsed.get("steps", steps)

        return {"type": _type, "complexity": complexity, "steps": steps}
    except Exception as e:
        logger.error(f"生成任务步骤失败：{e}。原始需求：{user_text}")
        return {"type": "task", "complexity": "low", "steps": [user_text.strip()]}

async def plan_task_steps_v2(
    ai_client: AIClient,
    user_text: str,
    enabled_tools: set = None,
    conversation_history: List[Dict] = None,
    user_raw_inputs: List[str] = None,
    skills_context: List[Dict] = None,
) -> dict:
    """新版：区分全局提示与可执行步骤，返回包含 system_prompt。

    目标：
    - 将策略性、通用性、跨步骤的指导性内容归入 `system_prompt`；
    - `steps` 仅保留具体、可执行的动作描述（动词开头，避免泛化建议）；
    - question 类型不拆分步骤，steps 为空数组。

    返回JSON示例：
    {
      "type": "task|question",
      "complexity": "low|high",
      "system_prompt": "全局指导性提示（不含具体执行动作）",
      "steps": ["动词开头的可执行步骤"]
    }
    """
    logger.debug("使用新版规划：区分系统提示与可执行步骤")
    try:
        sys_prompt = (
            "你是任务规划助手。严格区分‘全局提示’与‘可执行步骤’并输出JSON。\n"
            "- 全局提示（system_prompt）：包含策略、约束、注意事项、通用技巧，不是具体执行动作；\n"
            "- 可执行步骤（steps）：每项以动词开头，指向具体动作和目标，不含泛化词汇（例如‘尽量、建议、最好、可以考虑’）。严禁在步骤中出现具体查询语句、代码、命令或参数示例（例如包含引号包裹的参数、等号赋值、管道符串、示例SPL/SQL等）；如需执行查询，仅描述调用工具，参数在执行阶段再确定；\n"
            "- question 类型：不拆分步骤，steps 返回空数组；\n"
            "- 若技能详情中存在标注【重要】的前置动作（如查阅语法/示例），必须在 steps 中加入相应工具调用（不含参数示例）；\n"
            "- 最后一步必须为‘汇总结果并生成总结与后续建议’；\n"
            "- 使获取文档的步骤优先，排在其它步骤的前面；\n"
            "- 禁止使用Markdown代码块，必须仅输出一个合法JSON对象；\n"
            "- JSON键必须包含：type, complexity, system_prompt, steps；其中 steps 为字符串数组。\n"
            "- 输出前自检：括号匹配且可被解析。\n"
            "- 在生成的 system_prompt 中必须包含‘空结果处理策略’：当工具返回空结果/未查询到数据/黄色提示时，应放宽参数并重试，\n"
            "  不得复用与上一轮完全相同的参数；优先扩大时间范围（如 -2h/-6h）、使用模糊匹配（like/contains）、减少过滤条件、\n"
            "  必要时移除过严的 origin 过滤；重试次数不超过 2 次，每次重试要求在输出中标注 [STEP_RETRY] 并说明参数差异；\n"
            "  若连续两次仍为空，停止重试并给出原因分析与后续建议。\n"
            "JSON示例：{\n  \"type\": \"task|question\",\n  \"complexity\": \"low|high\",\n  \"system_prompt\": \"...\",\n  \"steps\": [\"...\"]\n}"
        )

        # 复用消息构造以携带会话与工具上下文
        messages = build_planning_messages(
            sys_prompt,
            user_text,
            enabled_tools=enabled_tools,
            conversation_history=conversation_history or [],
            user_raw_inputs=user_raw_inputs or [],
            skills_context=skills_context or [],
        )

        resp = await ai_client.chat_async(messages, temperature=0.0)
        raw = (getattr(resp, "content", "") or "").strip()
        logger.debug(f"新版规划原始回复：{raw}")
        raw = re.sub(r"^```json\s*|\s*```$", "", raw)
        import ast
        candidate = raw
        m = re.search(r"\{[\s\S]*\}", raw)
        if m:
            candidate = m.group(0)
        data: Dict[str, Any] = {}
        try:
            data = json.loads(candidate)
        except Exception:
            try:
                data = ast.literal_eval(candidate)
            except Exception:
                data = {}

        if not isinstance(data, dict):
            data = {}

        # 提取字段并规范化
        _type_raw = str((data.get("type") or "").strip().lower())
        is_question = _type_raw in ("question", "问题", "qa", "问答")
        _type = "question" if is_question else "task"
        complexity = str((data.get("complexity") or "low").strip().lower() or "low")
        system_prompt_out = str((data.get("system_prompt") or "").strip())
        raw_steps = data.get("steps")

        steps: List[str] = []
        if is_question:
            steps = []
        else:
            if isinstance(raw_steps, list):
                for item in raw_steps:
                    if isinstance(item, str):
                        txt = item.strip()
                        if txt:
                            steps.append(txt)
            elif isinstance(raw_steps, str):
                for ln in raw_steps.splitlines():
                    ln = ln.strip()
                    if ln:
                        steps.append(ln)

        # 进一步规范化逻辑已移除，保留模型原始步骤文本

        # 移除自动前置 get_docs 步骤的本地逻辑，统一由模型在提示中自行决定

        # 追加总结步骤（若缺失）
        try:
            has_summary = any(re.search(r"总结|汇总|归纳|结论", x or "") for x in steps)
            if not has_summary:
                steps.append("汇总查询结果，生成总结与后续建议")
        except Exception:
            steps.append("汇总查询结果，生成总结与后续建议")

        result = {
            "type": _type,
            "complexity": complexity,
            "system_prompt": system_prompt_out,
            "steps": steps,
        }
        return result
    except Exception as e:
        logger.error(f"新版生成任务步骤失败：{e}。原始需求：{user_text}")
        return {
            "type": "task",
            "complexity": "low",
            "system_prompt": "",
            "steps": [user_text.strip()],
        }

def get_enabled_tools_openai_format(enabled_tools: set) -> list:
    """获取已启用工具的OpenAI格式定义列表
    
    从全局工具注册表中筛选出已启用的工具，并返回其OpenAI格式定义。
    
    Args:
        enabled_tools: 已启用工具的集合
        
    Returns:
        list: 已启用工具的OpenAI格式定义列表，如果出错则返回空列表
    """
    try:
        all_tools = function_registry.get_openai_tools_format() or []
        if not enabled_tools:
            return []
        filtered = []
        for t in all_tools:
            fn = (t or {}).get("function", {})
            nm = fn.get("name")
            if nm and nm in enabled_tools:
                filtered.append(t)
        return filtered
    except Exception:
        return []

async def process_planning_response(
    ai_client: AIClient,
    raw_text: Optional[str],
    steps: Optional[List[str]],
    user_text: str,
    task_type: str,
    enabled_tools: Optional[set] = None,
) -> Dict[str, Any]:
    """统一解析与整炼任务步骤，返回 {'steps': List[str]}。

    - 若提供 raw_text，则先解析 JSON/文本，得到初步 steps；
    - 然后向 AI 发送整炼请求，返回更精确、清晰、可执行的 steps；
    - 任一步失败都会回退到可用的结果。
    """
    parsed_steps: List[str] = list(steps or [])

    # 1) 解析 raw_text（如果有）
    if raw_text:
        try:
            cleaned = re.sub(r"^```json\s*|\s*```$", "", raw_text.strip())
            cleaned = re.sub(r"\[(?:PLAN_READY|PLAY_READY|STEP_DONE|STEP_CONTINUE|STEP_REQUIRE_USER|step_done|step_continue|step_require_user)\]", "", cleaned)
            import ast
            candidate = cleaned
            m = re.search(r"\{[\s\S]*\}", cleaned)
            if m:
                candidate = m.group(0)
            data = None
            try:
                data = json.loads(candidate)
            except Exception:
                try:
                    data = ast.literal_eval(candidate)
                except Exception:
                    data = None
            if isinstance(data, dict):
                raw_steps = data.get("steps")
                if isinstance(raw_steps, list):
                    parsed_steps = []
                    for item in raw_steps:
                        if isinstance(item, str) and item.strip():
                            parsed_steps.append(item.strip())
                        elif isinstance(item, dict):
                            for key in ("step", "text", "description"):
                                v = item.get(key)
                                if isinstance(v, str) and v.strip():
                                    parsed_steps.append(v.strip())
                                    break
                elif isinstance(raw_steps, str):
                    lines = [ln.strip() for ln in raw_steps.splitlines() if ln.strip()]
                    parsed_steps = []
                    for ln in lines:
                        ln = re.sub(r"^\s*[\-\*\u2022]+\s*", "", ln)
                        ln = re.sub(r"^\s*\d+[\.\)]\s*", "", ln)
                        if ln:
                            parsed_steps.append(ln)
            else:
                raise ValueError("planning json parse failed")
        except Exception:
            lines = [ln.strip() for ln in (raw_text or "").splitlines() if ln.strip()]
            parsed_steps = []
            for ln in lines:
                if re.match(r'^\s*(\{|\}|\[|\]|```|"?complexity"?\s*:|"?steps"?\s*:)', ln):
                    continue
                ln2 = re.sub(r"^\s*[\-\*\u2022]+\s*", "", ln)
                ln2 = re.sub(r"^\s*\d+[\.\)]\s*", "", ln2)
                if ln2:
                    parsed_steps.append(ln2)

    if not parsed_steps:
        parsed_steps = [user_text.strip()]

    # 2) 整炼步骤
    try:
        refine_prompt = (
            "你是任务步骤整炼助手。请将给定的初始步骤整理成精确、清晰、可执行的步骤。\n"
            "要求：\n"
            "1) 每一步使用动词开头，描述具体可执行动作；\n"
            "2) 避免笼统描述与省略，补全必要参数或对象；\n"
            "3) 如需要工具调用，请明确函数名与关键参数；\n"
            "4) 不要编号或添加额外标记；\n"
            "仅输出JSON：{\"steps\": [\"...\"]}，且不使用Markdown代码块。"
        )
        refine_messages = [
            {"role": "system", "content": refine_prompt},
            {"role": "user", "content": (
                f"任务类型: {task_type}\n"
                f"用户需求: {user_text}\n"
                f"已启用工具: {', '.join(enabled_tools or []) or '无'}\n"
                f"初始步骤(JSON数组)：\n{json.dumps(parsed_steps, ensure_ascii=False)}"
            )},
        ]
        resp2 = await ai_client.chat_async(refine_messages, temperature=0.0)
        raw2 = (getattr(resp2, 'content', '') or '').strip()
        logger.debug(f"二次整理步骤原始回复：{raw2}")
        raw2 = re.sub(r"^```json\s*|\s*```$", "", raw2)
        refined_steps: List[str] = []
        try:
            data2 = json.loads(raw2)
            if isinstance(data2, dict):
                rs = data2.get("steps")
                if isinstance(rs, list):
                    for item in rs:
                        if isinstance(item, str):
                            txt = item.strip()
                            if txt:
                                txt = re.sub(r"^\s*[\-\*\u2022]+\s*", "", txt)
                                txt = re.sub(r"^\s*\d+[\.\)]\s*", "", txt)
                                refined_steps.append(txt)
            if refined_steps:
                return {"steps": refined_steps}
        except Exception:
            pass
    except Exception as e:
        logger.warning(f"二次整理步骤失败：{e}")
    return {"steps": parsed_steps}



def requires_user_confirmation(text: str) -> bool:
    """判断AI响应是否需要用户确认或输入
    
    分析AI响应文本，判断是否包含需要用户确认或输入的提示。
    
    Args:
        text: AI响应文本
        
    Returns:
        bool: 是否需要用户确认或输入
    """
    if not text:
        return False
    
    # 检查是否包含明确的用户输入请求
    input_patterns = [
        r"请输入",
        r"请提供",
        r"需要你[的]?(输入|确认)",
        r"请选择",
        r"你想要[的]?(\w+)吗",
        r"你需要[的]?(\w+)吗",
        r"你希望[的]?(\w+)吗",
        r"是否继续",
        r"是否需要",
        r"是否要",
        r"你确定",
        r"请确认",
    ]
    
    for pattern in input_patterns:
        if re.search(pattern, text):
            return True
    
    # 检查是否包含问句
    question_patterns = [
        r"\?$",
        r"？$",
        r"请问",
        r"如何选择",
        r"怎么选择",
        r"要选择哪个",
    ]
    
    for pattern in question_patterns:
        if re.search(pattern, text):
            return True
    
    return False

async def process_tool_calls(
    tool_calls: List[Dict], 
    chat_history_widget=None, 
    add_to_base_messages: bool = True
) -> List[Dict]:
    """处理工具调用并展示结果
    
    执行工具调用，并将结果添加到聊天历史和基础消息列表中。
    
    Args:
        tool_calls: 工具调用列表
        chat_history_widget: 聊天历史控件
        add_to_base_messages: 是否将工具结果添加到基础消息列表
        
    Returns:
        List[Dict]: 工具结果消息列表，可添加到基础消息中
    """
    tool_messages = []
    
    if not tool_calls:
        return tool_messages
    
    tool_results = await function_executor.execute_from_tool_calls_async(tool_calls)
    
    for i, tool_result in enumerate(tool_results):
        tool_call = tool_calls[i]
        fn = tool_call.get("function", {})
        func_name = fn.get("name")
        func_args = fn.get("arguments", "{}")
        
        if tool_result.get("success"):
            val = tool_result.get("result", "")
            if isinstance(val, (dict, list)):
                try:
                    result_str = json.dumps(val, ensure_ascii=False)
                except Exception:
                    result_str = str(val)
                result_obj_for_ui = val if isinstance(val, dict) else None
            elif isinstance(val, Widget):
                result_str = "(图表可视化结果)"
                result_obj_for_ui = val
            else:
                result_str = str(val) if val is not None else ""
                result_obj_for_ui = None
                
            if not result_str.strip():
                result_str = "(结果为空)"
                
            compressed_text, was_compressed = compress_if_large(result_str, threshold=8000)
            
            if chat_history_widget:
                chat_history_widget.add_tool_call(
                    func_name,
                    func_args,
                    compressed_text if was_compressed else result_str,
                    True,
                    result_obj=result_obj_for_ui,
                )
                
            if add_to_base_messages:
                tool_msg = {
                    "role": "tool",
                    "tool_call_id": tool_call.get("id", f"call_{func_name}"),
                    "content": compressed_text if was_compressed else result_str
                }
                tool_messages.append(tool_msg)
        else:
            err = tool_result.get("error", "执行失败")
            
            if chat_history_widget:
                chat_history_widget.add_tool_call(func_name, func_args, err, False)
                
            if add_to_base_messages:
                tool_msg = {
                    "role": "tool",
                    "tool_call_id": tool_call.get("id", f"call_{func_name}"),
                    "content": err or ""
                }
                tool_messages.append(tool_msg)
                
    return tool_messages


def needs_tool_call(content: str) -> bool:
    """检测是否需要工具调用（增强版）
    
    目标：减少漏判，让常见数据检索/列表类请求自动走工具通道。
    """
    try:
        text = (content or "").strip()
    except Exception:
        text = ""
    if not text:
        return False

    # 基础关键字（中英文）
    base_keywords = [
        "搜索", "查询", "获取", "执行", "调用", "运行", "查看", "看下", "列出", "列表", "统计", "top", "limit",
        "search", "query", "get", "execute", "call", "run", "smart_search"
    ]

    # 常见模式：前N条、最近N条、limit N
    import re
    patterns = [
        r"前\s*\d+\s*条",
        r"最近\s*\d+\s*条",
        r"limit\s*\d+",
    ]

    text_lower = text.lower()
    if any(k in text for k in base_keywords) or any(re.search(p, text_lower) for p in patterns):
        return True

    # 涉及明显数据域词汇时也倾向使用工具
    domain_hints = ["事件", "日志", "记录", "仓库", "repo", "数据", "表", "查询语句"]
    if any(h in text for h in domain_hints):
        return True

    return False

# -------------------- 新增：通知过滤与单次工具执行 --------------------

def filter_notification(message: Any, kwargs: Dict[str, Any], debug_markers: Tuple[str, ...] = ()) -> Tuple[bool, Dict[str, Any]]:
    """过滤通知，仅保留重要信息并屏蔽明显调试噪音。
    
    返回值：
    - should_send: 是否应发送通知
    - prepared_kwargs: 传递给 notify 的参数（确保 markup=False，限制长度等）
    """
    try:
        text = str(message or "")
    except Exception:
        text = ""

    # 屏蔽明显的调试/噪音标记
    try:
        for mark in (debug_markers or ()):  # e.g. "DEBUG", emojis
            if mark and mark in text:
                return False, {}
    except Exception:
        pass

    # 仅展示重要等级（error/warning/success）
    severity = (kwargs or {}).get("severity")
    important = {"error", "warning", "success"}
    if not severity or str(severity) not in important:
        # 无等级或非重要等级，默认不展示
        return False, {}

    # 规范化参数：禁用富文本，限制超长消息
    prepared = dict(kwargs or {})
    prepared.setdefault("markup", False)
    try:
        if len(text) > 2000:
            text = text[:2000] + " …"
    except Exception:
        pass
    # 保留原 severity/timeout 等
    return True, prepared

async def execute_tool_call(
    tool_call: Dict[str, Any],
    tools: List[Dict[str, Any]],
    chat_history_widget,
    messages: List[Dict[str, Any]],
    *,
    tool_executor=None,
    notifier=None,
) -> Dict[str, Any]:
    """执行单个工具调用，更新UI与消息历史，并返回结果。
    
    参数：
    - tool_call: 单个OpenAI风格的工具调用对象
    - tools: 提供给模型的工具定义列表（此处仅用于上下文，不强制校验）
    - chat_history_widget: 聊天历史控件（用于展示工具执行结果）
    - messages: 对话消息列表（将在末尾追加 tool 消息）
    - tool_executor: 可选的执行器（无则使用全局 function_executor）
    - notifier: 可选的通知函数（如 app.notify）
    
    返回：
    - dict，包含 "tool_message" 与 "result" 两项，便于上层记录
    """
    try:
        fn = (tool_call or {}).get("function", {})
        func_name = fn.get("name")
        func_args = fn.get("arguments", "{}")
        if not func_name:
            raise ValueError("缺少函数名")

        # 执行工具调用（复用批量接口执行单项，保持一致的错误处理与超时策略）
        execu = tool_executor if tool_executor is not None else function_executor
        results = await execu.execute_from_tool_calls_async([tool_call])
        tool_result = results[0] if results else {"success": False, "error": "执行器未返回结果"}

        import json as _json
        if tool_result.get("success"):
            val = tool_result.get("result", "")
            if isinstance(val, Widget):
                result_str = "(图表可视化结果)"
                result_obj_for_ui = val
            elif isinstance(val, (dict, list)):
                try:
                    result_str = _json.dumps(val, ensure_ascii=False)
                except Exception:
                    result_str = str(val)
                result_obj_for_ui = val if isinstance(val, dict) else None
            else:
                result_str = str(val) if val is not None else ""
                result_obj_for_ui = None
            if not result_str.strip():
                result_str = "(结果为空)"

            compressed_text, was_compressed = compress_if_large(result_str, threshold=8000)
            if chat_history_widget:
                chat_history_widget.add_tool_call(
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
                if notifier:
                    notifier(f"✅ 工具 {func_name} 执行成功", timeout=2)
            except Exception:
                pass
        else:
            error_msg = tool_result.get("error", "执行失败") or "执行失败"
            if not error_msg.strip():
                error_msg = "(错误信息为空)"
            if chat_history_widget:
                chat_history_widget.add_tool_call(func_name, func_args, error_msg, False)
            tool_message = {
                "role": "tool",
                "tool_call_id": tool_call.get("id", f"call_{func_name}"),
                "content": error_msg,
            }
            messages.append(tool_message)
            try:
                if notifier:
                    notifier(f"❌ 工具 {func_name} 执行失败：{error_msg}", severity="warning", timeout=4, markup=False)
            except Exception:
                pass

        return {"tool_message": tool_message, "result": tool_result}
    except Exception as e:
        # 捕获异常也作为失败的工具消息写入，避免对话中断
        try:
            fn = (tool_call or {}).get("function", {})
            func_name = fn.get("name") or "unknown"
            func_args = fn.get("arguments", "{}")
        except Exception:
            func_name, func_args = "unknown", "{}"
        err_text = f"工具执行异常: {e}"
        if chat_history_widget:
            try:
                chat_history_widget.add_tool_call(func_name, func_args, err_text, False)
            except Exception:
                pass
        tool_message = {
            "role": "tool",
            "tool_call_id": (tool_call or {}).get("id", f"call_{func_name}"),
            "content": err_text,
        }
        try:
            messages.append(tool_message)
        except Exception:
            pass
        try:
            if notifier:
                notifier(f"❌ 工具 {func_name} 执行异常：{e}", severity="warning", timeout=4, markup=False)
        except Exception:
            pass
        return {"tool_message": tool_message, "result": {"success": False, "error": err_text}}


def build_planning_messages(prompt: str, user_text: str, enabled_tools: set = None, conversation_history: List[Dict] = None, user_raw_inputs: List[str] = None, skills_context: List[Dict] = None) -> List[Dict]:
    # 用户历史摘要（优先原始输入）
    try:
        user_history_text = build_user_raw_inputs_summary(
            user_raw_inputs or [],
            current_task_text=user_text,
        )
        if user_history_text == "无":
            user_history_text = build_user_history_summary(
                conversation_history,
                current_task_text=user_text,
                exclude_synthetic=True,
            )
    except Exception:
        user_history_text = build_user_history_summary(
            conversation_history,
            current_task_text=user_text,
            exclude_synthetic=True,
        )
    messages = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": f"可用工具：{', '.join(enabled_tools or []) or '无'}\n用户当前任务：{user_text}\n用户历史输入：\n{user_history_text}"}
    ]
    # 附加技能上下文摘要（如果有），提升规划对技能权限与白名单的感知
    try:
        lines: List[str] = []
        for s in (skills_context or []):
            try:
                nm = (s or {}).get("name") or ""
                summ = (s or {}).get("summary") or ""
                perm = ",".join((s or {}).get("permissions") or [])
                tw = ",".join((s or {}).get("tools_whitelist") or [])
                lines.append(f"技能: {nm} | 摘要: {summ} | 权限: {perm or '无'} | 白名单工具: {tw or '无'}")
            except Exception:
                continue
        if lines:
            messages.append({
                "role": "user",
                "content": "[技能上下文摘要]\n" + "\n".join(lines[:6])
            })
        # 追加技能详情，帮助模型参考完整能力说明
        detail_blocks: List[str] = []
        for s in (skills_context or []):
            try:
                nm = (s or {}).get("name") or ""
                summ = (s or {}).get("summary") or ""
                perms = ", ".join((s or {}).get("permissions") or [])
                tools = ", ".join((s or {}).get("tools_whitelist") or [])
                desc = (s or {}).get("description") or ""
                if isinstance(desc, str) and len(desc) > 1500:
                    desc = desc[:1500] + "..."
                block = (
                    f"技能名称: {nm}\n"
                    f"技能摘要: {summ}\n"
                    f"权限: {perms or '无'}\n"
                    f"工具白名单: {tools or '无'}\n"
                    f"技能说明: {desc or '无'}"
                )
                detail_blocks.append(block)
            except Exception:
                continue
        if detail_blocks:
            messages.append({
                "role": "user",
                "content": "[技能详情]\n" + "\n\n".join(detail_blocks)
            })
    except Exception:
        pass
    # 附加最近的工具上下文摘要以提升规划准确性
    try:
        ctx_snippets: List[str] = []
        hist = list(conversation_history or [])
        count = 0
        for idx in range(len(hist) - 1, -1, -1):
            msg = hist[idx]
            if isinstance(msg, dict) and msg.get("role") == "tool":
                txt = (msg.get("content") or "").strip()
                if txt:
                    ctx_snippets.append(txt[:600])
                    count += 1
                    if count >= 3:
                        break
        if ctx_snippets:
            ctx_text = "\n\n".join(reversed(ctx_snippets))
            messages.append({
                "role": "user",
                "content": f"[上下文工具结果摘要]\n{ctx_text}"
            })
    except Exception:
        pass
    logger.debug(f"任务规划提示词：{messages}")
    return messages


async def convert_to_expected_format(
    ai_client: AIClient,
    raw_text: str,
    system_prompt: str,
    expected_format: str,
    conversation_history: List[Dict] = None,
    raw_inputs: List[str] = None,
    skills_context: List[Dict] = None,
) -> Dict[str, Any]:
    """将原始文本转换为指定的预期格式（通用）。

    参数：
    - raw_text: 原始文本（可能包含代码块或标记）
    - system_prompt: 用于指导转换的系统提示词（含约束与规范）
    - expected_format: 期望的输出格式示例或描述（例如JSON样例）

    返回：
    - Dict[str, Any]: 解析后的结构化结果；若解析失败则返回空字典
    """
    try:
        # 优化：显式给出预期JSON示例，并强化合法性与自检要求，避免模型返回不完整JSON
        sys_prompt = (
            f"{system_prompt}\n"
            "你需要将用户输入转换为一个完整且合法的JSON对象。\n"
            "- 仅输出一个JSON对象，不要附加任何解释或额外文本。\n"
            "- 不使用Markdown代码块（不要输出```json或```）。\n"
            "- JSON必须包含键: type, complexity, steps；其中steps为字符串数组。\n"
            "- 输出前自检：括号需成对匹配，最后一个字符必须是}\u007d，JSON可被解析。\n"
            "- 若不确定，请返回一个最小合法对象：{\"type\": \"task\", \"complexity\": \"low\", \"steps\": []}。\n"
            "参考以下预期格式示例，并严格按示例结构与键名输出：\n"
            f"{expected_format}\n"
            "若提供技能上下文，请优先参考其摘要、权限与工具白名单来设计步骤与选择工具。"
        )
        # 优先使用原始输入摘要，其次回退到会话历史解析
        try:
            user_history_text = build_user_raw_inputs_summary(
                raw_inputs or [],
                current_task_text=raw_text if raw_text else None,
            )
            if user_history_text == "无":
                user_history_text = build_user_history_summary(
                    conversation_history or [],
                    current_task_text=raw_text if raw_text else None,
                    exclude_synthetic=True,
                )
        except Exception:
            user_history_text = build_user_history_summary(
                conversation_history or [],
                current_task_text=raw_text if raw_text else None,
                exclude_synthetic=True,
            )
        
        # 提取最近一次模型返回文本（优先assistant，其次tool），并限制长度
        try:
            last_model_text = "无"
            hist = list(conversation_history or [])
            for idx in range(len(hist) - 1, -1, -1):
                msg = hist[idx]
                if isinstance(msg, dict) and msg.get("role") == "assistant":
                    t = (msg.get("content") or "").strip()
                    if t:
                        last_model_text = t[-1200:]
                        break
            if last_model_text == "无":
                for idx in range(len(hist) - 1, -1, -1):
                    msg = hist[idx]
                    if isinstance(msg, dict) and msg.get("role") == "tool":
                        t = (msg.get("content") or "").strip()
                        if t:
                            last_model_text = t[-800:]
                            break
        except Exception:
            last_model_text = "无"
        
        # 构建技能上下文文本（若提供）
        skills_text = ""
        try:
            sc = list(skills_context or [])
            if sc:
                lines = ["[技能上下文]"] if len(sc) == 1 else ["[多技能上下文]"]
                for item in sc:
                    name = item.get("name", "")
                    summary = item.get("summary", "")
                    perms = ", ".join(item.get("permissions", []) or [])
                    tools = ", ".join(item.get("tools_whitelist", []) or [])
                    desc = item.get("description", "")
                    block = (
                        f"- name: {name}\n"
                        f"  summary: {summary}\n"
                        f"  permissions: {perms}\n"
                        f"  tools_whitelist: {tools}\n"
                        f"  description:\n{desc}\n"
                    )
                    lines.append(block)
                skills_text = "\n" + "\n".join(lines)
        except Exception:
            skills_text = ""

        messages = [
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": (
                f"当前消息：\n{raw_text}\n\n"
                f"用户历史输入：\n{user_history_text}\n\n"
                f"最近一次模型返回:\n{last_model_text}{skills_text}"
            )},
        ]
        logger.debug(f"格式转换提示词：{json.dumps(messages, ensure_ascii=False, indent=2)}")
        resp = await ai_client.chat_async(messages, temperature=0.0)
        logger.debug(f"格式转换回复原始：{resp}")
        content = (getattr(resp, 'content', '') or '').strip()
        logger.debug(f"格式转换回复：{json.dumps(content, ensure_ascii=False, indent=2)}")
        content = re.sub(r"^```json\s*|\s*```$", "", content)
        content = re.sub(r"\[(?:PLAN_READY|PLAY_READY|STEP_DONE|STEP_CONTINUE|STEP_REQUIRE_USER|step_done|step_continue|step_require_user)\]", "", content)
        # 优先提取最可能的JSON对象子串，避免尾部混入标记
        import ast
        candidate = content
        m = re.search(r"\{[\s\S]*\}", content)
        if m:
            candidate = m.group(0)
        try:
            data = json.loads(candidate)
            if isinstance(data, dict):
                return data
        except Exception:
            logger.warning(f"直接解析JSON失败，尝试使用ast.literal_eval：{candidate}")
            try:
                data = ast.literal_eval(candidate)
                if isinstance(data, dict):
                    return data
            except Exception:
                logger.warning(f"ast.literal_eval也失败，返回空字典：{candidate}")
                pass
        return {}
    except Exception as e:
        logger.warning(f"转换到预期格式失败：{e}")
        return {}