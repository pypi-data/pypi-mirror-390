from re import T
from mando import command, arg
from ketacli.sdk.ai import AIClient, AIConfig, ResponseValidator, function_registry, function_executor
from rich.console import Console
from rich.live import Live
from rich.markdown import Markdown
from rich.panel import Panel
from ketacli.sdk.base.search import search_summary, search_spl
from ketacli.sdk.ai.tool_output_compressor import compress_if_large
import json
import os

console = Console()

@command
@arg("message", type=str, help="要发送给AI的消息", nargs="?")
@arg("-m", "--model", type=str, help="指定使用的模型名称")
@arg("--show-tools", action="store_true", help="显示可用工具列表")
@arg("--max-iterations", type=int, default=10, help="最大迭代次数")
@arg("--tools", type=str, help="启用的工具名（逗号分隔），使用'all'启用全部。默认与交互式一致")
def chat(message, system_prompt=None, model=None, max_iterations=10, show_tools=False, tools=None):
    """命令行模式：使用AI大模型进行智能function call对话
    
    :param message: 要发送给AI的消息（命令行模式必填）
    :param -m, --model: 指定使用的模型名称
    :param --system-prompt: 系统提示词
    :param --max-iterations: 最大迭代次数，防止无限循环
    :param --show-tools: 显示可用的工具列表
    :param --tools: 启用的工具名（逗号分隔），使用'all'启用全部。默认与交互式一致
    """
    
    # 与交互式一致的默认启用工具（参考 InteractiveChatApp.enabled_tools）
    DEFAULT_ENABLED_TOOLS = {
        "list_assets",
        "list_queryable_assets",
        "search_data_for_log",
        "search_data_for_metric",
        "get_repository_fields",
        "get_docs",
        # 图表渲染工具如需开放，可加入："display_chart_textual"
    }
    
    # 命令行模式必须提供消息
    if not message:
        console.print("[yellow]请提供消息内容。若要图形界面，请使用 ichat 命令。[/yellow]")
        return

    if not system_prompt:
        # 优先从 sdk/ai/prompts/system.md 读取系统提示词；
        # 若文件不存在则回退到内置默认提示词。
        prompt_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "../sdk/ai/prompts/system.md")
        )
        try:
            with open(prompt_path, "r", encoding="utf-8") as f:
                system_prompt = f.read().strip()
        except Exception:
            system_prompt = (
                "你是 Keta CLI 的智能助手，能够调用工具完成数据搜索、分析、列出资源、获取文档等任务。"
                "请在需要时使用可用的函数工具，并保持回答简洁、准确、可执行。"
            )
        
    try:        
        if show_tools:
            all_tools = function_registry.get_openai_tools_format() or []
            console.print("[bold blue]可用工具列表:[/bold blue]")
            for tool in all_tools:
                func_info = tool.get('function', {})
                name = func_info.get('name', '(未知)')
                console.print(Panel(
                    f"[bold green]{name}[/bold green]\n{func_info.get('description','')}\n\n"
                    f"[dim]参数: {json.dumps(func_info.get('parameters',{}), indent=2, ensure_ascii=False)}[/dim]",
                    title=f"工具: {name}"
                ))
            # 显示默认启用的工具集合提示
            default_preview = ", ".join(sorted(DEFAULT_ENABLED_TOOLS))
            console.print(f"\n[dim]默认启用（与交互式一致）: {default_preview}[/dim]")
            console.print("[dim]使用 --tools=all 或 --tools=name1,name2 自定义启用集合[/dim]")
            return
        
        # 创建AI客户端
        client = AIClient(system_prompt=system_prompt, model_name=model)
        
        # 获取全部工具定义
        all_tools = function_registry.get_openai_tools_format() or []

        # 解析启用工具集合
        if tools:
            selector = tools.strip()
            if selector.lower() == "all":
                enabled_tools = {
                    (t or {}).get("function", {}).get("name")
                    for t in all_tools if (t or {}).get("function", {}).get("name")
                }
            else:
                enabled_tools = {n.strip() for n in selector.split(",") if n.strip()}
        else:
            enabled_tools = set(DEFAULT_ENABLED_TOOLS)

        # 过滤得到最终提供给模型的工具列表
        def _filter_tools(tools_list, enabled_names):
            filtered = []
            for t in tools_list:
                fn = (t or {}).get("function", {})
                nm = fn.get("name")
                if nm and nm in enabled_names:
                    filtered.append(t)
            return filtered

        tools_for_model = _filter_tools(all_tools, enabled_tools)

        if not tools_for_model:
            console.print("[yellow]提示: 当前未启用任何工具或工具列表为空，将使用普通对话模式[/yellow]")
            # 使用普通对话模式（不带工具）
            response = client.chat(message)
            if response.content:
                console.print(f"[bold green]AI回复:[/bold green]")
                console.print(response.content, markup=False)
            if response.usage:
                console.print(f"\n[dim]Token使用统计: {response.usage}[/dim]")
            return
        
        # 初始化对话历史
        messages = [{"role": "user", "content": message}]
        
        console.print(f"[bold blue]开始AI Function Call对话 (模型: {client.get_current_model()})[/bold blue]")
        console.print(f"[dim]启用工具数量: {len(tools_for_model)}[/dim]\n")
        
        iteration = 0
        while iteration < max_iterations:
            iteration += 1
            console.print(f"[bold cyan]--- 第 {iteration} 轮对话 ---[/bold cyan]")
            
            # 发送请求
            response = client.chat_with_tools(
                messages=messages,
                tools=tools_for_model,
                tool_choice="auto"
            )
            
            # 添加AI响应到对话历史
            assistant_message = {
                "role": "assistant",
                "content": response.content
            }
            
            # 如果有tool_calls，添加到消息中
            if response.tool_calls:
                assistant_message["tool_calls"] = response.tool_calls
            
            messages.append(assistant_message)
            
            # 显示AI响应
            if response.content:
                console.print(f"[bold green]AI回复:[/bold green]")
                console.print(response.content, markup=False)
                console.print()
            
            # 处理工具调用（仅执行已启用的工具）
            if response.tool_calls:
                # 按启用集合过滤工具调用
                filtered_tool_calls = [
                    tc for tc in (response.tool_calls or [])
                    if ((tc or {}).get("function", {}).get("name") in enabled_tools)
                ]

                # 若存在未启用的工具调用，告知并忽略
                disabled_called = [
                    (tc or {}).get("function", {}).get("name")
                    for tc in (response.tool_calls or [])
                    if ((tc or {}).get("function", {}).get("name") not in enabled_tools)
                ]
                if disabled_called:
                    preview = ", ".join([n for n in disabled_called if n][:6])
                    console.print(f"[yellow]检测到未启用的工具调用已被忽略: {preview}[/yellow]")
                    # 若本轮仅包含未启用的工具调用且模型未返回文本内容，提供启用指引
                    try:
                        if (not filtered_tool_calls) and not (response.content or "").strip():
                            console.print(
                                f"[yellow]⚠️ 模型尝试调用未启用的工具: {preview}。该调用已被忽略。[/yellow]"
                            )
                            console.print(
                                "[dim]使用 --tools=all 启用全部工具，或 --tools=name1,name2 自定义启用；"
                                "可用工具用 --show-tools 查看。若使用图形界面，运行 ichat 并按 Ctrl+T 启用工具。[/dim]"
                            )
                    except Exception:
                        pass

                console.print(f"[bold yellow]AI请求调用 {len(filtered_tool_calls)} 个工具:[/bold yellow]")
                
                for tool_call in filtered_tool_calls:
                    if tool_call.get("type") == "function":
                        func_data = tool_call.get("function", {})
                        func_name = func_data.get("name")
                        func_args = func_data.get("arguments", "{}")
                        
                        console.print(f"[cyan]调用工具: {func_name}[/cyan]")
                        console.print(f"[dim]参数: {func_args}[/dim]")
                        
                        # 执行工具调用
                        try:
                            if isinstance(func_args, str):
                                args_dict = json.loads(func_args)
                            else:
                                args_dict = func_args
                            
                            # 获取并执行函数
                            func_schema = function_registry.get_function(func_name)
                            if func_schema:
                                result = func_schema.function(**args_dict)
                                console.print(f"[green]✓ 工具执行成功[/green]")
                                
                                # 压缩过大的工具结果
                                compressed_text, was_compressed = compress_if_large(result, threshold=8000)

                                # 将工具执行结果（可能已压缩）添加到对话历史
                                tool_message = {
                                    "role": "tool",
                                    "tool_call_id": tool_call.get("id", f"call_{func_name}"),
                                    "content": compressed_text
                                }
                                messages.append(tool_message)
                                
                                # 控制台展示摘要或原文
                                if was_compressed:
                                    console.print(f"[dim]结果已压缩并摘要展示:[/dim]", markup=False)
                                    console.print(compressed_text, markup=False)
                                else:
                                    if isinstance(result, str) and len(result) > 200:
                                        console.print(f"[dim]结果摘要: {result[:1000]}...[/dim]", markup=False)
                                    else:
                                        console.print(f"[dim]结果: {result}[/dim]", markup=False)
                            else:
                                console.print(f"[red]✗ 工具 {func_name} 未找到[/red]")
                                # 添加错误消息
                                tool_message = {
                                    "role": "tool",
                                    "tool_call_id": tool_call.get("id", f"call_{func_name}"),
                                    "content": f"错误: 工具 {func_name} 未找到"
                                }
                                messages.append(tool_message)
                                
                        except Exception as e:
                            console.print(f"[red]✗ 工具执行失败: {e}[/red]")
                            # 添加错误消息
                            tool_message = {
                                "role": "tool",
                                "tool_call_id": tool_call.get("id", f"call_{func_name}"),
                                "content": f"错误: {str(e)}"
                            }
                            messages.append(tool_message)
                
                console.print()
                # 继续下一轮对话，让AI处理工具调用结果
                continue
            else:
                # 没有工具调用，对话结束
                console.print("[bold green]对话完成[/bold green]")
                break
        
        if iteration >= max_iterations:
            console.print(f"[yellow]达到最大迭代次数 ({max_iterations})，对话结束[/yellow]")
        
        # 显示使用统计
        if response.usage:
            console.print(f"\n[dim]Token使用统计: {response.usage}[/dim]")
            
    except Exception as e:
        console.print(f"[red]AI Function Call失败: {e}[/red]")


@command
@arg("operation", type=str, nargs="?", completer=lambda prefix, **kwd: [x for x in ["list-skills", "show-skill", "reload-skills"] if x.startswith(prefix)])
@arg("name", type=str, nargs="?", help="技能名称（用于 show-skill）")
def ichat(operation, name, use_web=False, host="localhost", port=8000):
    """交互式界面与技能管理

    - 无 operation 时：启动 Textual 交互式聊天窗口
    - list-skills：列出技能元信息
    - show-skill <name>：懒加载并展示技能正文
    - reload-skills：重建索引并打印新增/移除/冲突摘要
    """
    # 分支：技能管理命令
    if operation in {"list-skills", "show-skill", "reload-skills"}:
        try:
            from rich.table import Table
            from ketacli.sdk.ai.skills.registry import SkillsRegistry
            from ketacli.sdk.ai.skills.loader import load_skill_by_name
            from ketacli.sdk.ai.skills import ENV_VAR_NAME, init_skills_environment
            from pathlib import Path
            import json

            # 显示目录来源（帮助定位与调试）
            init_skills_environment()

            registry = SkillsRegistry()
            registry.build()

            if operation == "list-skills":
                table = Table(title="技能列表（仅元信息）")
                table.add_column("name")
                table.add_column("summary")
                table.add_column("enabled")
                table.add_column("permissions")
                table.add_column("source_path")
                for m in registry.list_metas():
                    perms = ",".join(m.permissions or []) if m.permissions else ""
                    table.add_row(m.name, m.summary or "", str(m.enabled), perms, m.source_path or "")
                console.print(table)
                # 若存在错误或冲突，输出摘要
                summary = registry.summary()
                if summary:
                    console.print(Panel(summary, title="摘要", border_style="yellow"))
                return

            if operation == "show-skill":
                if not name:
                    console.print("[red]请指定技能名称: ketacli ichat show-skill <name>[/red]")
                    return
                skill = load_skill_by_name(name)
                if not skill:
                    console.print(f"[red]未找到技能: {name}[/red]")
                    return
                # 展示正文（全部）与权限/工具白名单
                console.print(Panel(Markdown(skill.description or ""), title=f"技能: {skill.meta.name}"))
                perms = ", ".join(skill.meta.permissions or []) if skill.meta.permissions else "(无)"
                tools = ", ".join(skill.meta.tools_whitelist or []) if skill.meta.tools_whitelist else "(未限制)"
                console.print(f"[dim]permissions: {perms}[/dim]")
                console.print(f"[dim]tools_whitelist: {tools}[/dim]")
                return

            if operation == "reload-skills":
                # 读取旧快照
                cache_path = Path.home() / ".ketacli" / "skills_index.json"
                try:
                    old = json.loads(cache_path.read_text("utf-8")) if cache_path.exists() else {}
                    old_names = set(old.get("names", []))
                except Exception:
                    old_names = set()

                # 当前索引
                metas = registry.list_metas()
                cur_names = {m.name for m in metas}

                # Diff
                added = sorted(list(cur_names - old_names))
                removed = sorted(list(old_names - cur_names))

                console.print(Panel("技能索引已重建", title="reload-skills", border_style="green"))
                if added:
                    console.print(f"[green]新增: {', '.join(added)}[/green]")
                if removed:
                    console.print(f"[yellow]移除: {', '.join(removed)}[/yellow]")
                summary = registry.summary()
                if summary:
                    console.print(Panel(summary, title="冲突/错误摘要", border_style="yellow"))
                else:
                    console.print("[dim]无冲突或解析错误[/dim]")

                # 写入新快照
                try:
                    cache_path.parent.mkdir(parents=True, exist_ok=True)
                    cache = {"names": sorted(list(cur_names))}
                    cache_path.write_text(json.dumps(cache, ensure_ascii=False, indent=2), "utf-8")
                except Exception:
                    console.print("[yellow]写入快照失败[/yellow]")
                return

        except Exception as e:
            console.print(f"[red]技能命令执行失败: {e}[/red]")
        return

    # 分支：无 operation，启动交互式聊天窗口
    try:
        from ketacli.sdk.textual_chart.app import run_interactive_chat
        console.print("[bold green]启动交互式AI对话窗口...[/bold green]")
        if use_web:
            console.print("[bold yellow]注意: 启用Web模式后，将在浏览器中打开对话窗口[/bold yellow]")
            from textual_serve.server import Server
            import sys
            command = f"{sys.executable} -m ketacli ichat"
            server = Server(command, host=host, port=port, title="KetaOps AI Chat")
            server.serve()
        else:
            run_interactive_chat()
    except ImportError as e:
        console.print(f"[red]无法启动交互式模式: {e}[/red]")
        console.print("[yellow]请确保已安装textual依赖[/yellow]")
    except Exception as e:
        console.print(f"[red]交互式模式启动失败: {e}[/red]")


@command
@arg("action", type=str, help="操作类型 (list|add|remove|set-default)", default="list")
def ai_config(action, model_name=None, endpoint=None, api_key=None):
    """管理AI模型配置
    
    :param action: 操作类型 (list|add|remove|set-default)
    :param -m, --model-name: 模型名称
    :param -e, --endpoint: API端点地址
    :param -k, --api-key: API密钥
    """
    try:
        # 对于add操作，允许空配置；其他操作需要有效配置
        allow_empty = (action == "add")
        config = AIConfig(allow_empty=allow_empty)
        
        if action == "list":
            models = config.list_models()
            default_model = config.get_default_model()
            
            console.print("[bold]可用的AI模型:[/bold]")
            for model in models:
                marker = " [green](默认)[/green]" if model == default_model else ""
                console.print(f"  • {model}{marker}")
                
        elif action == "add":
            if not all([model_name, endpoint, api_key]):
                console.print("[red]添加模型需要提供 --model-name, --endpoint 和 --api-key 参数[/red]")
                return
                
            from ketacli.sdk.ai.config import AIModelConfig
            model_config = AIModelConfig(
                name=model_name,
                endpoint=endpoint,
                api_key=api_key,
                model=model_name
            )
            config.add_model(model_config)
            console.print(f"[green]已添加模型: {model_name}[/green]")
            
        elif action == "remove":
            if not model_name:
                console.print("[red]删除模型需要提供 --model-name 参数[/red]")
                return
                
            config.remove_model(model_name)
            console.print(f"[green]已删除模型: {model_name}[/green]")
            
        elif action == "set-default":
            if not model_name:
                console.print("[red]设置默认模型需要提供 --model-name 参数[/red]")
                return
                
            config.set_default_model(model_name)
            console.print(f"[green]已设置默认模型: {model_name}[/green]")
            
        else:
            console.print("[red]无效的操作类型，支持: list, add, remove, set-default[/red]")
            
    except Exception as e:
        console.print(f"[red]配置操作失败: {e}[/red]")