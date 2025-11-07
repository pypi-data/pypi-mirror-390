"""YAML 加载器（阶段1）

- 扫描 YAML 文件仅解析元信息（SkillMeta），并保存 `source_path`；
- 懒加载：在选择技能时按 `source_path` 读取 `description` 并构造完整 `Skill`；
- 校验：必填字段缺失、重复 name、解析异常给出清晰错误信息。
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Iterable, List, Optional, Tuple

import yaml

from .models import SkillMeta, Skill
from . import get_all_skills_dirs


def _builtin_example_dir() -> str:
    return str((Path(__file__).parent / "examples").resolve())


def _iter_yaml_files(dirs: Iterable[str]) -> Iterable[str]:
    exts = {".yaml", ".yml"}
    for d in dirs:
        if not d:
            continue
        dd = os.path.abspath(os.path.expanduser(d))
        if not os.path.isdir(dd):
            continue
        # 只扫描顶层目录的 YAML 文件
        for name in os.listdir(dd):
            fp = os.path.join(dd, name)
            if os.path.isfile(fp) and os.path.splitext(name)[1].lower() in exts:
                yield fp


def _parse_meta(path: str) -> SkillMeta:
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except Exception as e:
        raise ValueError(f"解析 YAML 失败: {path} -> {e}")

    if not isinstance(data, dict):
        raise ValueError(f"YAML 格式错误(非对象): {path}")

    name = data.get("name")
    summary = data.get("summary")
    if not name or not isinstance(name, str):
        raise ValueError(f"缺少或非法字段 'name': {path}")
    if not summary or not isinstance(summary, str):
        raise ValueError(f"缺少或非法字段 'summary': {path}")

    enabled = data.get("enabled", True)
    triggers = data.get("triggers")
    permissions = data.get("permissions")
    tools_whitelist = data.get("tools_whitelist")

    # 轻量类型校验与规整：列表元素需为字符串，自动去除两端空白
    def _as_list_str(x, field_name: str):
        if x is None:
            return None
        if isinstance(x, list):
            result: list[str] = []
            for i, v in enumerate(x):
                if not isinstance(v, str):
                    raise ValueError(
                        f"字段'{field_name}'需为字符串列表: {path} -> 索引{i}类型={type(v).__name__}"
                    )
                s = v.strip()
                if s:
                    result.append(s)
            return result
        raise ValueError(f"字段'{field_name}'需为字符串列表: {path}")

    meta = SkillMeta(
        name=name,
        summary=summary,
        enabled=bool(enabled),
        triggers=_as_list_str(triggers, "triggers"),
        permissions=_as_list_str(permissions, "permissions"),
        tools_whitelist=_as_list_str(tools_whitelist, "tools_whitelist"),
        source_path=os.path.abspath(path),
    )
    return meta


def _collect_metas_from_dirs(dirs: Iterable[str]) -> Tuple[List[SkillMeta], List[str]]:
    """扫描目录并解析元信息，返回 (metas, errors)。不在此处做重名检测。"""
    metas: List[SkillMeta] = []
    errors: List[str] = []
    for path in _iter_yaml_files(dirs):
        try:
            meta = _parse_meta(path)
            metas.append(meta)
        except Exception as e:
            errors.append(str(e))
    return metas, errors


def default_search_dirs() -> List[str]:
    """返回默认扫描目录列表（内置示例 + 用户默认 + 环境变量）。"""
    return [_builtin_example_dir(), *get_all_skills_dirs(include_defaults=True)]


def scan_metas(search_dirs: Optional[List[str]] = None) -> Tuple[List[SkillMeta], List[str]]:
    """扫描指定目录集合，返回 (metas, errors)。不做重名检测。"""
    dirs = search_dirs or default_search_dirs()
    return _collect_metas_from_dirs(dirs)


def load_metas() -> List[SkillMeta]:
    """扫描默认目录并返回 SkillMeta 列表。

    默认目录包含：
    - 内置示例目录：`ketacli/sdk/ai/skills/examples`
    - 用户默认目录与环境变量目录：`~/.ketacli/skills` 与 `KETACLI_SKILLS_DIRS`
    若存在错误（解析失败、缺失字段、重复 name），将抛出包含详情的异常。
    """
    search_dirs = default_search_dirs()
    metas, errors = scan_metas(search_dirs)
    # 重名检测（此函数抛异常，供 CLI 或直接加载时阻断）
    name_to_paths: dict[str, List[str]] = {}
    for m in metas:
        name_to_paths.setdefault(m.name, []).append(m.source_path or "")
    dup_msgs: List[str] = []
    for name, paths in name_to_paths.items():
        if len(paths) > 1:
            dup_msgs.append(f"重复 name '{name}':\n  - " + "\n  - ".join(paths))
    if errors or dup_msgs:
        raise ValueError("\n".join([*errors, *dup_msgs]))
    return metas


def load_skill_by_name(name: str) -> Optional[Skill]:
    """按名称懒加载完整 Skill（含 description）。

    若存在重名，将抛出异常并列出冲突路径；若未找到则返回 None。
    """
    metas = load_metas()
    candidates = [m for m in metas if m.name == name]
    if not candidates:
        return None
    if len(candidates) > 1:
        paths = [m.source_path or "" for m in candidates]
        raise ValueError(f"存在重名技能 '{name}':\n  - " + "\n  - ".join(paths))

    meta = candidates[0]
    assert meta.source_path, "meta 缺少 source_path"
    try:
        with open(meta.source_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except Exception as e:
        raise ValueError(f"读取 description 失败: {meta.source_path} -> {e}")

    description = data.get("description") if isinstance(data, dict) else None
    if description is None:
        # description 缺失不强制报错，返回空描述
        description = ""
    return Skill(meta=meta, description=description)