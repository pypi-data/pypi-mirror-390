"""技能自动选择器

基于 SkillMeta 的 `triggers`、`name`、`summary` 进行简单匹配，选择最合适的技能。
规则：
- 仅考虑 `enabled=True` 的技能
- 主要依据 `triggers`（大小写不敏感的子串匹配），每命中一个触发词+2分
- 次要依据 `name` 与 `summary`（每命中+1分）
- 返回分数最高且分数>0 的技能
"""

from __future__ import annotations

from typing import List, Optional, Any, Dict
import json
import logging
import re

logger = logging.getLogger("ketacli.textual.ai_helpers")

def _safe_json_loads(text: str) -> Dict:
    """宽容解析模型返回的JSON，自动剥离```json代码块与前后噪音。
    返回字典；失败则返回空字典。
    """
    if not text:
        return {}
    s = text.strip()
    # 去掉```json/``` 包裹
    if s.startswith("```"):
        try:
            s = s.strip().strip("`")
            # 去掉可能的语言标记，如json
            if s.lower().startswith("json"):
                s = s[4:].strip()
        except Exception:
            pass
    # 粗略截取第一个{到最后一个}
    try:
        l = s.find("{")
        r = s.rfind("}")
        if l != -1 and r != -1 and r > l:
            s = s[l:r+1]
    except Exception:
        pass
    try:
        return json.loads(s)
    except Exception:
        return {}

from .models import SkillMeta


def _norm(text: str) -> str:
    return (text or "").strip().lower()

# 轻量停用词（中英文混合），用于过滤通用性极强、易引发误命中的词
STOPWORDS = {
    # 中文常用泛词
    "查询", "搜索", "查找", "日志", "指标", "数据", "结果", "请问", "帮我", "一下", "怎么", "如何", "查看", "展示", "显示", "统计", "分析", "情况", "信息", "内容",
    # 英文常见泛词
    "search", "query", "log", "logs", "metric", "metrics", "data", "result", "results", "show", "display", "view", "find", "help", "please", "how", "check", "list",
}

def _tokens(text: str) -> List[str]:
    """粗粒度分词：
    - 英文/数字：使用正则提取连续的字母数字下划线
    - 中文：保留原字符串整体作为token（不引入分词依赖）
    最终用于强命中的精确匹配；停用词会在后续过滤。
    """
    s = _norm(text)
    ascii_tokens = re.findall(r"[a-z0-9_]+", s)
    # 对于包含空白的情况，额外按空格切分（兼容混合输入）
    space_tokens = [t for t in s.split() if t]
    # 合并并去重
    tokens = list({*ascii_tokens, *space_tokens})
    return tokens


def score_skill(user_text: str, meta: SkillMeta) -> tuple[int, dict]:
    """
    计算技能与用户输入的匹配分，并返回细节：
    - 触发词子串命中 +2/次
    - 名称子串命中 +1
    - 摘要子串命中 +1
    """
    text = _norm(user_text)
    name_n = _norm(meta.name)
    summ_n = _norm(meta.summary or "")

    # 分词并过滤停用词（仅影响强命中）
    tokens = [t for t in _tokens(text) if t and t not in STOPWORDS]
    token_set = set(tokens)

    strong_hits = 0
    weak_hits = 0
    for t in (meta.triggers or []):
        tt = _norm(t)
        if not tt:
            continue
        # 强命中：精确token命中，或中文/长词(>=3)的子串命中
        if tt in token_set or (len(tt) >= 3 and tt in text):
            strong_hits += 1
        # 弱命中：其余子串命中（避免短词造成过度匹配）
        elif tt and tt in text:
            weak_hits += 1

    name_hit = 1 if name_n and name_n in text else 0
    summary_hit = 1 if summ_n and summ_n in text else 0
    # 权重：强命中+3，弱命中+1，名称/摘要各+1
    score = strong_hits * 3 + weak_hits * 1 + name_hit + summary_hit
    detail = {
        "score": score,
        "strong_hits": strong_hits,
        "weak_hits": weak_hits,
        "name_hit": bool(name_hit),
        "summary_hit": bool(summary_hit),
        "tokens": tokens,
    }
    return score, detail


def select_best_skill(user_text: str, metas: List[SkillMeta]) -> Optional[SkillMeta]:
    text = _norm(user_text)
    if not text:
        return None
    best: Optional[SkillMeta] = None
    best_score: int = 0
    for meta in metas or []:
        if not getattr(meta, "enabled", True):
            continue
        score, _ = score_skill(text, meta)
        if score > best_score:
            best = meta
            best_score = score
    return best if best_score > 0 else None

def select_best_skill_with_explain(user_text: str, metas: List[SkillMeta]) -> Dict:
    """返回最佳技能及评分细节，便于调试或日志记录。
    结构：{"best": SkillMeta|None, "detail": {"score": int, ...}}
    """
    text = _norm(user_text)
    if not text:
        return {"best": None, "detail": {"score": 0}}
    best: Optional[SkillMeta] = None
    best_detail: Dict = {"score": 0}
    for meta in metas or []:
        if not getattr(meta, "enabled", True):
            continue
        score, detail = score_skill(text, meta)
        if score > best_detail.get("score", 0):
            best = meta
            best_detail = {**detail, "name": meta.name}
    return {"best": best if (best_detail.get("score", 0) > 0) else None, "detail": best_detail}


async def select_skills_by_model(ai_client: Any, user_text: str, metas: List[SkillMeta]) -> Dict[str, Any]:
    """首选使用大模型从候选SkillMeta中选择技能；无法确定时由上层回退。

    返回结构：{"mode": "none|single|multi", "selected": [name,...], "reason": str}
    - none：模型判断不需要技能（如闲聊）
    - single/multi：选择一个或多个技能名
    """
    # 仅注入必要字段，避免token浪费
    candidates = [
        {
            "name": m.name,
            "summary": (m.summary or ""),
            "enabled": bool(getattr(m, "enabled", True)),
        }
        for m in (metas or [])
        if getattr(m, "enabled", True)
    ]
    if not candidates or not (user_text or "").strip():
        return {"mode": "none", "selected": [], "reason": "空输入或无候选"}

    system_prompt = (
        "你是技能选择器。给定用户输入与候选技能列表(仅name/summary)，"
        "请基于语义匹配选择最合适的技能；如果是闲聊/问候等无需技能，选择none。"
        "技能可以选择多个，当用户需求需要同时满足多个技能时，mode选择multi。"
        "仅输出JSON，不要额外文本，不要使用Markdown代码块。格式："
        "{\"mode\": \"none|single|multi\", \"selected\": [\"技能名\"...], \"reason\": \"简短理由\"}。"
    )
    content = (
        "[用户输入]\n" + (user_text or "") + "\n\n" +
        "[候选技能]\n" + json.dumps(candidates, ensure_ascii=False)
    )
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": content},
    ]
    try:
        resp = await ai_client.chat_async(messages, temperature=0.0)
        raw = (getattr(resp, "content", "") or "").strip()
        data = _safe_json_loads(raw)
        mode = str(data.get("mode", "")).strip().lower()
        selected = [str(x).strip() for x in (data.get("selected") or []) if str(x).strip()]
        reason = str(data.get("reason", "")).strip()
        if mode not in {"none", "single", "multi"}:
            # 简单纠错：根据数量修正模式
            mode = "none" if not selected else ("single" if len(selected) == 1 else "multi")
        return {"mode": mode, "selected": selected, "reason": reason, "raw": raw}
    except Exception:
        # 失败时由上层回退
        return {"mode": "none", "selected": [], "reason": "模型选择失败"}


def select_skills_by_model_sync(ai_client: Any, user_text: str, metas: List[SkillMeta]) -> Dict[str, Any]:
    """同步版本：使用 AIClient.chat 进行技能选择，便于在同步事件中调用。

    返回结构同异步版本。
    """
    candidates = [
        {
            "name": m.name,
            "summary": (m.summary or ""),
            "enabled": bool(getattr(m, "enabled", True)),
        }
        for m in (metas or [])
        if getattr(m, "enabled", True)
    ]
    if not candidates or not (user_text or "").strip():
        return {"mode": "none", "selected": [], "reason": "空输入或无候选"}

    system_prompt = (
        "你是技能选择器。给定用户输入与候选技能列表(仅name/summary)，"
        "请基于语义匹配选择最合适的技能；如果是闲聊/问候等无需技能，选择none。"
        "技能可以选择多个，当用户需求需要同时满足多个技能时，mode选择multi。"
        "仅输出JSON，不要额外文本，不要使用Markdown代码块。格式："
        "{\"mode\": \"none|single|multi\", \"selected\": [\"技能名\"...], \"reason\": \"简短理由\"}。"
    )
    content = (
        "[用户输入]\n" + (user_text or "") + "\n\n" +
        "[候选技能]\n" + json.dumps(candidates, ensure_ascii=False)
    )
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": content},
    ]
    try:
        logger.info(f"select_skills_by_model_sync: messages={messages}")
        resp = ai_client.chat(messages, temperature=0.0)
        raw = (getattr(resp, "content", "") or "").strip()
        logger.info(f"select_skills_by_model_sync: raw={raw}")
        data = _safe_json_loads(raw)
        mode = str(data.get("mode", "")).strip().lower()
        selected = [str(x).strip() for x in (data.get("selected") or []) if str(x).strip()]
        reason = str(data.get("reason", "")).strip()
        if mode not in {"none", "single", "multi"}:
            mode = "none" if not selected else ("single" if len(selected) == 1 else "multi")
        return {"mode": mode, "selected": selected, "reason": reason, "raw": raw}
    except Exception:
        return {"mode": "none", "selected": [], "reason": "模型选择失败"}