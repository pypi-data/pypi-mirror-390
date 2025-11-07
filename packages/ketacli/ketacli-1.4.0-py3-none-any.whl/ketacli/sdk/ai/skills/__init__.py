"""Skills 包初始化与环境目录解析

阶段0目标：
- 建立 `ketacli.sdk.ai.skills` 包结构；
- 约定默认用户技能目录与环境变量 `KETACLI_SKILLS_DIRS`；
- 提供解析函数，后续 CLI 与注册表可复用；

不在导入时产生副作用输出，验证时可显式调用 `init_skills_environment()`。
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import List


# 环境变量名称与默认用户技能目录
ENV_VAR_NAME = "KETACLI_SKILLS_DIRS"
DEFAULT_USER_SKILLS_DIR = str(Path.home() / ".ketacli" / "skills")


def _split_env_paths(value: str) -> List[str]:
    """按":"分隔 env 路径，展开用户目录与相对路径为绝对路径。"""
    parts = [p for p in value.split(":") if p]
    normalized: List[str] = []
    for p in parts:
        expanded = os.path.expanduser(p)
        normalized.append(os.path.abspath(expanded))
    return normalized


def get_default_dirs() -> List[str]:
    """返回默认用户技能目录列表。"""
    return [os.path.abspath(os.path.expanduser(DEFAULT_USER_SKILLS_DIR))]


def get_env_dirs() -> List[str]:
    """读取 `KETACLI_SKILLS_DIRS` 并解析为目录列表。若未设置，返回空列表。"""
    value = os.environ.get(ENV_VAR_NAME, "").strip()
    return _split_env_paths(value) if value else []


def get_all_skills_dirs(include_defaults: bool = True) -> List[str]:
    """合并默认目录与环境变量目录，去重保持顺序。"""
    dirs: List[str] = []
    if include_defaults:
        dirs.extend(get_default_dirs())
    dirs.extend(get_env_dirs())

    # 去重保持顺序
    seen = set()
    unique_dirs: List[str] = []
    for d in dirs:
        if d not in seen:
            seen.add(d)
            unique_dirs.append(d)
    return unique_dirs


def init_skills_environment() -> List[str]:
    """
    初始化并打印技能目录来源，返回解析后的目录列表。
    供阶段0验证使用；后续 CLI/Registry 可复用该函数输出目录来源。
    """
    dirs = get_all_skills_dirs(include_defaults=True)
    print(
        f"[ketacli.skills] ENV {ENV_VAR_NAME}='" + os.environ.get(ENV_VAR_NAME, "") + "'"
    )
    print("[ketacli.skills] resolved skills dirs:")
    for i, d in enumerate(dirs, start=1):
        print(f"  {i}. {d}")
    return dirs


# 暴露常用符号
__all__ = [
    "ENV_VAR_NAME",
    "DEFAULT_USER_SKILLS_DIR",
    "get_default_dirs",
    "get_env_dirs",
    "get_all_skills_dirs",
    "init_skills_environment",
]