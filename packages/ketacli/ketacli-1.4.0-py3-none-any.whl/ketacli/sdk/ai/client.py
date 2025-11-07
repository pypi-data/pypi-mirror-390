"""
AI大模型请求客户端

提供统一的AI大模型调用接口，支持多种模型和验证机制。
"""

import requests
import json
import time
import asyncio
import aiohttp
from typing import Dict, Any, Optional, Callable, Union, List
from dataclasses import dataclass
from rich.console import Console
from .config import AIConfig, AIModelConfig
from .validators import ResponseValidator
from .function_call import function_registry

# 创建console实例用于调试日志
console = Console(markup=False)


@dataclass
class AIRequest:
    """AI请求数据结构"""
    messages: list
    model: Optional[str] = None
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None
    stream: bool = False
    tools: Optional[List[Dict[str, Any]]] = None
    tool_choice: Optional[Union[str, Dict[str, Any]]] = None
    extra_params: Optional[Dict[str, Any]] = None


@dataclass
class AIResponse:
    """AI响应数据结构"""
    content: str
    raw_response: Dict[str, Any]
    model: str
    usage: Optional[Dict[str, Any]] = None
    finish_reason: Optional[str] = None
    request_id: Optional[str] = None
    tool_calls: Optional[List[Dict[str, Any]]] = None


class AIClient:
    """AI大模型请求客户端"""
    
    def __init__(self, config_path: str = None, model_name: str = None, system_prompt: str = None):
        """
        初始化AI客户端
        
        Args:
            config_path: 配置文件路径
            model_name: 模型名称，如果为None则使用默认模型
            system_prompt: 系统提示词，将在每次对话开始时自动添加
        """
        self.config_manager = AIConfig(config_path)
        self.model_name = model_name or self.config_manager.get_default_model()
        self.model_config = self.config_manager.get_model_config(self.model_name)
        self.system_prompt = system_prompt
        self.session = requests.Session()
        
        # 设置默认请求头
        if self.model_config.headers:
            self.session.headers.update(self.model_config.headers)
        
        # 设置认证
        self._setup_auth()
    
    def _setup_auth(self):
        """设置认证信息"""
        if self.model_config.api_key:
            if 'openai' in self.model_name.lower():
                self.session.headers['Authorization'] = f'Bearer {self.model_config.api_key}'
            elif 'claude' in self.model_name.lower() or 'anthropic' in self.model_name.lower():
                self.session.headers['x-api-key'] = self.model_config.api_key
            else:
                # 通用认证方式
                self.session.headers['Authorization'] = f'Bearer {self.model_config.api_key}'
    
    def _prepare_request_data(self, request: AIRequest) -> Dict[str, Any]:
        """
        准备请求数据
        
        Args:
            request: AI请求对象
            
        Returns:
            Dict: 请求数据
        """
        data = {
            'model': request.model or self.model_config.model,
            'max_tokens': request.max_tokens or self.model_config.max_tokens,
            'temperature': request.temperature or self.model_config.temperature,
        }
        
        # 更健壮的提供商识别：优先使用配置中的 provider，其次回退到模型名
        provider = ''
        try:
            provider = getattr(self.model_config, 'provider', '') or ''
        except Exception:
            provider = ''
        provider_lc = (provider or self.model_name or '').lower()

        # 根据不同的模型类型处理消息格式
        if ('claude' in provider_lc) or ('anthropic' in provider_lc):
            # Claude API格式 - 特殊处理
            if request.messages:
                # 转换消息格式
                if len(request.messages) == 1 and request.messages[0].get('role') == 'user':
                    data['messages'] = request.messages
                else:
                    data['messages'] = request.messages
            # 支持流式标志
            if request.stream:
                data['stream'] = True
            # 传递工具定义与选择策略（Claude/Anthropic 支持 tool use）
            if request.tools:
                data['tools'] = request.tools
            if request.tool_choice is not None:
                data['tool_choice'] = request.tool_choice
        else:
            # 默认使用OpenAI格式 (适用于OpenAI、DeepSeek、Qwen、通义千问等大部分模型)
            data['messages'] = request.messages
            if request.stream:
                data['stream'] = True
            # 添加tools支持
            if request.tools:
                data['tools'] = request.tools
            if request.tool_choice is not None:
                data['tool_choice'] = request.tool_choice
        
        # 添加额外参数
        if request.extra_params:
            data.update(request.extra_params)
        
        if self.model_config.extra_params:
            data.update(self.model_config.extra_params)        
        return data
    
    def _parse_response(self, response: requests.Response) -> AIResponse:
        """
        解析响应数据
        
        Args:
            response: HTTP响应对象
            
        Returns:
            AIResponse: 解析后的AI响应对象
        """
        try:
            response_data = response.json()
        except json.JSONDecodeError:
            raise Exception(f"无法解析响应JSON: {response.text}")
        
        # 根据不同模型解析响应
        if 'openai' in self.model_name.lower():
            return self._parse_openai_response(response_data)
        elif 'claude' in self.model_name.lower() or 'anthropic' in self.model_name.lower():
            return self._parse_claude_response(response_data)
        else:
            return self._parse_generic_response(response_data)
    
    def _parse_openai_response(self, data: Dict[str, Any]) -> AIResponse:
        """解析OpenAI响应"""
        if 'choices' not in data or not data['choices']:
            raise Exception("OpenAI响应中没有choices字段")
        
        choice = data['choices'][0]
        message = choice.get('message', {})
        content = message.get('content', '')
        finish_reason = choice.get('finish_reason')
        tool_calls = message.get('tool_calls')
        # 当OpenAI未返回结构化tool_calls但以文本标记给出时，尝试解析文本
        if not tool_calls and content:
            
            parsed = self._parse_tool_calls_from_text(content)
            if parsed:
                tool_calls = parsed
        
        # 清理文本中的工具标记块，避免展示污染
        try:
            import re
            t = content or ""
            t = t.replace("｜", "|").replace("▁", "_")
            patterns = [
                r"<\|\s*tool[\s_]*calls[\s_]*begin\s*\|>",
                r"<\|\s*tool[\s_]*calls[\s_]*end\s*\|>",
                r"\|\s*<\s*tool[\s_]*calls[\s_]*begin\s*>\s*\|",
                r"\|\s*<\s*tool[\s_]*calls[\s_]*end\s*>\s*\|",
            ]
            for p in patterns:
                t = re.sub(p, "", t, flags=re.IGNORECASE)
            # 移除工具调用块内容
            t = re.sub(r"<\|\s*tool\s*_call\s*_begin\s*\|>.*?<\|\s*tool\s*_call\s*_end\s*\|>", "", t, flags=re.DOTALL | re.IGNORECASE)
            t = re.sub(r"\|\s*<\s*tool\s*_call[\s_]*begin\s*>\s*\|.*?\|\s*<\s*tool\s*_call[\s_]*end\s*>\s*\|", "", t, flags=re.DOTALL | re.IGNORECASE)
            content = t.strip()
        except Exception:
            pass
        
        return AIResponse(
            content=content,
            raw_response=data,
            model=data.get('model', self.model_config.model),
            usage=data.get('usage'),
            finish_reason=finish_reason,
            request_id=data.get('id'),
            tool_calls=tool_calls
        )
    
    def _parse_claude_response(self, data: Dict[str, Any]) -> AIResponse:
        """解析Claude响应"""
        if 'content' not in data:
            raise Exception("Claude响应中没有content字段")
        
        content_list = data['content']
        if isinstance(content_list, list) and content_list:
            content = content_list[0].get('text', '')
        else:
            content = str(content_list)
        
        return AIResponse(
            content=content,
            raw_response=data,
            model=data.get('model', self.model_config.model),
            usage=data.get('usage'),
            finish_reason=data.get('stop_reason'),
            request_id=data.get('id')
        )
    
    def _parse_tool_calls_from_text(self, content: str) -> Optional[List[Dict[str, Any]]]:
        """从文本内容中解析工具调用

        支持两类文本格式：
        1) 直接函数调用格式：fn({json})
        2) 标记格式：<|tool_call_begin|> fn <|tool_sep|> {json} <|tool_call_end|>
        设计划重点：
        - 通用、无方法名特例：仅做格式统一与类型泛化
        - 名称归一：驼峰→下划线、分隔符→下划线、小写
        - 参数键归一与类型泛化：按注册schema将键归一、类型转换、补足必填
        """
        import re
        import json

        if not content:
            return None

        # 标记归一：全角竖线 → ASCII 竖线，特殊下划线符号“ ” → "_"；
        # 同时去除无用的外层 <|tool_calls_begin|> / <|tool_calls_end|>
        def _normalize_markers(text: str) -> str:
            try:
                t = text or ""
            except Exception:
                return text
            t = t.replace("｜", "|")
            t = t.replace("▁", "_")
            # 去除外层 calls 包裹以降低正则复杂度（兼容多种写法与空格/下划线混用）
            patterns = [
                r"<\|\s*tool[\s_]*calls[\s_]*begin\s*\|>",
                r"<\|\s*tool[\s_]*calls[\s_]*end\s*\|>",
                r"\|\s*<\s*tool[\s_]*calls[\s_]*begin\s*>\s*\|",
                r"\|\s*<\s*tool[\s_]*calls[\s_]*end\s*>\s*\|",
            ]
            for p in patterns:
                t = re.sub(p, "", t, flags=re.IGNORECASE)
            return t

        content = _normalize_markers(content)

        tool_calls: List[Dict[str, Any]] = []

        # 通用名称归一：驼峰→下划线；分隔符(., -, /, 空格)→下划线；小写；去重下划线
        def _normalize_name(name: str) -> str:
            try:
                n = (name or "").strip()
            except Exception:
                n = ""
            if not n:
                return n
            n = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", n)
            n = re.sub(r"[\.\-/\s]+", "_", n)
            n = n.lower()
            n = re.sub(r"_+", "_", n).strip("_")
            return n

        # 通用键归一：对参数键应用与名称相同的归一策略
        def _normalize_key(k: str) -> str:
            return _normalize_name(k)

        # 类型泛化与必填补足（基于函数schema，通用而非特定函数）
        def _normalize_args(func: str, args: Any) -> Dict[str, Any]:
            # 非字典统一包裹
            if not isinstance(args, dict):
                return {"value": args}
            a = {}
            for k, v in args.items():
                a[_normalize_key(k)] = v

            # 尝试获取函数schema
            func_schema = None
            try:
                func_schema = function_registry.get_function(func)
            except Exception:
                func_schema = None

            if not func_schema or not isinstance(func_schema.parameters, dict):
                return a

            params = func_schema.parameters or {}
            props = params.get("properties", {}) or {}
            required = params.get("required", []) or []

            # 通用类型转换：依据schema类型将字符串转换为目标类型
            def coerce_value(value: Any, typ: str) -> Any:
                if typ == "boolean":
                    if isinstance(value, bool):
                        return value
                    if isinstance(value, str):
                        s = value.strip().lower()
                        if s in {"true", "1", "yes", "y"}:
                            return True
                        if s in {"false", "0", "no", "n"}:
                            return False
                    if isinstance(value, (int, float)):
                        return bool(value)
                    return value
                if typ == "integer":
                    if isinstance(value, int):
                        return value
                    if isinstance(value, str):
                        try:
                            return int(value.strip())
                        except Exception:
                            return value
                    if isinstance(value, float):
                        return int(value)
                    return value
                if typ == "number":
                    if isinstance(value, (int, float)):
                        return float(value)
                    if isinstance(value, str):
                        try:
                            return float(value.strip())
                        except Exception:
                            return value
                    return value
                if typ == "array":
                    if isinstance(value, list):
                        return value
                    if isinstance(value, str):
                        # 通用：逗号分隔视为数组；否则单值数组
                        parts = [p.strip() for p in value.split(",")]
                        parts = [p for p in parts if p]
                        return parts if len(parts) > 1 else [value]
                    return [value]
                # 默认原样返回
                return value

            # 按schema转换已提供的属性类型
            for k in list(a.keys()):
                if k in props:
                    typ = props.get(k, {}).get("type")
                    if isinstance(typ, str):
                        a[k] = coerce_value(a[k], typ)

            # 补足必填：若缺失必填键，通用地从“未知键”中挑选类型匹配值赋入
            missing = [rk for rk in required if rk not in a]
            if missing:
                # 候选：不在props中的键或已在props但类型不匹配的值
                candidate_keys = [ck for ck in a.keys() if ck not in props]
                # 若无候选，则不做补足
                for rk in missing:
                    rk_typ = props.get(rk, {}).get("type", "string")
                    chosen_key = None
                    # 先找类型严格匹配的候选
                    for ck in candidate_keys:
                        v = a.get(ck)
                        vv = coerce_value(v, rk_typ)
                        # 若转换结果类型合理（例如字符串转换仍为字符串、数字成功转换），则选用
                        if rk_typ == "array" and isinstance(vv, list):
                            chosen_key = ck
                            break
                        if rk_typ == "integer" and isinstance(vv, int):
                            chosen_key = ck
                            break
                        if rk_typ == "number" and isinstance(vv, float):
                            chosen_key = ck
                            break
                        if rk_typ == "boolean" and isinstance(vv, bool):
                            chosen_key = ck
                            break
                        if rk_typ == "string" and isinstance(vv, str):
                            # 对字符串，偏向较长文本（更可能是表达式/查询）
                            chosen_key = ck if (chosen_key is None or len(str(v)) > len(str(a.get(chosen_key)))) else chosen_key
                    # 若未找到严格匹配，以第一个候选兜底
                    if chosen_key is None and candidate_keys:
                        chosen_key = candidate_keys[0]
                    # 执行赋值与移除候选键
                    if chosen_key is not None:
                        a[rk] = coerce_value(a[chosen_key], rk_typ)
                        candidate_keys.remove(chosen_key)
                        a.pop(chosen_key, None)

            return a

        # 1) 解析“函数名(JSON)”样式
        func_pattern = r'(\w+)\s*\(\s*({[^}]+})\s*\)'
        func_matches = re.findall(func_pattern, content)
        for i, (function_name, args_str) in enumerate(func_matches):
            try:
                args_obj = json.loads(args_str)
            except Exception:
                continue
            canonical = _normalize_name(function_name)
            norm_args = _normalize_args(canonical, args_obj)
            tool_calls.append({
                "id": f"call_{len(tool_calls)}_{canonical}",
                "type": "function",
                "function": {
                    "name": canonical,
                    "arguments": json.dumps(norm_args, ensure_ascii=False)
                }
            })

        # 2) 解析“工具标记”样式
        marker_block_pattern = r'<\|\s*tool_call_begin\s*\|>(.*?)<\|\s*tool_call_end\s*\|>'
        marker_blocks = re.findall(marker_block_pattern, content, flags=re.DOTALL)
        for block in marker_blocks:
            parts = re.split(r'(?:<\|\s*tool_sep\s*\|>|\|\s*<\s*tool_sep\s*>\s*\|)', block, maxsplit=1)
            if len(parts) != 2:
                continue
            func_name_raw = parts[0].strip().strip('|').strip()
            args_str = parts[1].strip()
            args_str = re.sub(r'^```[a-zA-Z0-9_\-]*\n', '', args_str)
            args_str = re.sub(r"```\s*$", '', args_str)
            try:
                args_obj = json.loads(args_str)
            except json.JSONDecodeError:
                cleaned = args_str.replace("'", '"')
                cleaned = re.sub(r',\s*}', '}', cleaned)
                try:
                    args_obj = json.loads(cleaned)
                except json.JSONDecodeError:
                    continue
            canonical = _normalize_name(func_name_raw)
            norm_args = _normalize_args(canonical, args_obj)
            tool_calls.append({
                "id": f"call_{len(tool_calls)}_{canonical}",
                "type": "function",
                "function": {
                    "name": canonical,
                    "arguments": json.dumps(norm_args, ensure_ascii=False)
                }
            })

        return tool_calls if tool_calls else None

    def _parse_generic_response(self, data: Dict[str, Any]) -> AIResponse:
        """解析通用响应"""
        content = ''
        finish_reason = None
        tool_calls = None
        
        # 首先尝试OpenAI格式 (choices[0].message.content)
        if 'choices' in data and data['choices'] and len(data['choices']) > 0:
            choice = data['choices'][0]
            if 'message' in choice:
                message = choice['message']
                if 'content' in message:
                    content = message['content']
                finish_reason = choice.get('finish_reason')
                # 提取tool_calls
                if 'tool_calls' in message:
                    tool_calls = message['tool_calls']
        
        # 如果没有找到，尝试其他可能的内容字段
        if not content:
            for field in ['content', 'text', 'response', 'output']:
                if field in data:
                    content = str(data[field])
                    break
        
        # 如果没有找到标准格式的tool_calls，但有content，尝试从content中解析工具调用
        if not tool_calls and content:
            tool_calls = self._parse_tool_calls_from_text(content)
        
        # 清理文本中的工具标记块，避免展示污染
        try:
            import re
            t = content or ""
            t = t.replace("｜", "|").replace("▁", "_")
            patterns = [
                r"<\|\s*tool[\s_]*calls[\s_]*begin\s*\|>",
                r"<\|\s*tool[\s_]*calls[\s_]*end\s*\|>",
                r"\|\s*<\s*tool[\s_]*calls[\s_]*begin\s*>\s*\|",
                r"\|\s*<\s*tool[\s_]*calls[\s_]*end\s*>\s*\|",
            ]
            for p in patterns:
                t = re.sub(p, "", t, flags=re.IGNORECASE)
            # 移除工具调用块内容
            t = re.sub(r"<\|\s*tool\s*_call\s*_begin\s*\|>.*?<\|\s*tool\s*_call\s*_end\s*\|>", "", t, flags=re.DOTALL | re.IGNORECASE)
            t = re.sub(r"\|\s*<\s*tool\s*_call[\s_]*begin\s*>\s*\|.*?\|\s*<\s*tool\s*_call[\s_]*end\s*>\s*\|", "", t, flags=re.DOTALL | re.IGNORECASE)
            content = t.strip()
        except Exception:
            pass
        
        return AIResponse(
            content=content,
            raw_response=data,
            model=data.get('model', self.model_config.model),
            usage=data.get('usage'),
            finish_reason=finish_reason or data.get('finish_reason'),
            request_id=data.get('id'),
            tool_calls=tool_calls
        )
    
    def chat(self, 
             messages: Union[str, list], 
             model: str = None,
             max_tokens: int = None,
             temperature: float = None,
             validator: ResponseValidator = None,
             callback: Callable[[AIResponse], Any] = None,
             **kwargs) -> AIResponse:
        """
        发送聊天请求
        
        Args:
            messages: 消息内容，可以是字符串或消息列表
            model: 模型名称
            max_tokens: 最大token数
            temperature: 温度参数
            validator: 响应验证器
            callback: 响应回调函数
            **kwargs: 其他参数
            
        Returns:
            AIResponse: AI响应对象
        """

        # 处理消息格式
        if isinstance(messages, str):
            messages = [{"role": "user", "content": messages}]
        
        # 如果设置了系统提示词，且消息列表中没有系统消息，则添加系统提示词
        if self.system_prompt:
            if not messages or messages[0].get("role") != "system":
                messages.insert(0, {"role": "system", "content": self.system_prompt})
        
        
        # 创建请求对象
        request = AIRequest(
            messages=messages,
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            extra_params=kwargs
        )
        
        return self.send_request(request, validator, callback)
    
    def chat_with_tools(self, 
                       messages: Union[str, list], 
                       tools: List[Dict[str, Any]] = None,
                       tool_choice: Union[str, Dict[str, Any]] = None,
                       model: str = None,
                       max_tokens: int = None,
                       temperature: float = None,
                       validator: ResponseValidator = None,
                       callback: Callable[[AIResponse], Any] = None,
                       **kwargs) -> AIResponse:
        """
        发送带有工具调用的聊天请求
        
        Args:
            messages: 消息内容，可以是字符串或消息列表
            tools: 可用工具列表
            tool_choice: 工具选择策略
            model: 模型名称
            max_tokens: 最大token数
            temperature: 温度参数
            validator: 响应验证器
            callback: 响应回调函数
            **kwargs: 其他参数
            
        Returns:
            AIResponse: AI响应对象
        """
        # 处理消息格式
        if isinstance(messages, str):
            messages = [{"role": "user", "content": messages}]
        
        # 如果设置了系统提示词，且消息列表中没有系统消息，则添加系统提示词
        if self.system_prompt:
            if not messages or messages[0].get("role") != "system":
                messages.insert(0, {"role": "system", "content": self.system_prompt})
        
        # 创建请求对象
        request = AIRequest(
            messages=messages,
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            tools=tools,
            tool_choice=tool_choice,
            extra_params=kwargs
        )
        
        return self.send_request(request, validator, callback)
    
    def send_request(self, 
                    request: AIRequest, 
                    validator: ResponseValidator = None,
                    callback: Callable[[AIResponse], Any] = None) -> AIResponse:
        """
        发送AI请求
        
        Args:
            request: AI请求对象
            validator: 响应验证器
            callback: 响应回调函数
            
        Returns:
            AIResponse: AI响应对象
        """
        
        try:
            # 准备请求数据
            request_data = self._prepare_request_data(request)
            
            response = self.session.post(
                self.model_config.endpoint,
                json=request_data,
                timeout=self.model_config.timeout
            )

            # 检查HTTP状态
            if not response.ok:
                console.print(f"[bold red][DEBUG][/bold red] HTTP请求失败: {response.status_code}")
                console.print(f"[bold red][DEBUG][/bold red] 错误响应内容: {response.text[:500]}...")
                raise Exception(f"HTTP请求失败: {response.status_code} - {response.text}")
            
            
            # 解析响应
            ai_response = self._parse_response(response)
            
            # 验证响应
            if validator:
                is_valid, errors = validator.validate(ai_response.raw_response)
                if not is_valid:
                    raise Exception(f"响应验证失败: {'; '.join(errors)}")
            
            # 执行回调
            if callback:
                callback(ai_response)
            
            return ai_response
            
        except requests.exceptions.Timeout:
            raise Exception(f"请求超时 ({self.model_config.timeout}秒)")
        except requests.exceptions.ConnectionError:
            raise Exception("连接错误，请检查网络和端点地址")
            raise
        except Exception as e:
            console.print(f"[bold red][DEBUG][/bold red] 请求异常: {type(e).__name__}: {e}")
            # raise Exception(f"AI请求失败: {e}")
            raise
    
    def stream_chat(self, 
                   messages: Union[str, list],
                   model: str = None,
                   max_tokens: int = None,
                   temperature: float = None,
                   callback: Callable[[str], None] = None,
                   **kwargs):
        """
        流式聊天请求
        
        Args:
            messages: 消息内容
            model: 模型名称
            max_tokens: 最大token数
            temperature: 温度参数
            callback: 流式数据回调函数
            **kwargs: 其他参数
            
        Yields:
            str: 流式响应内容片段
        """
        
        # 处理消息格式
        if isinstance(messages, str):
            messages = [{"role": "user", "content": messages}]
        
        
        # 如果设置了系统提示词，且消息列表中没有系统消息，则添加系统提示词
        if self.system_prompt and (not messages or messages[0].get("role") != "system"):
            messages.insert(0, {"role": "system", "content": self.system_prompt})

        # 创建请求对象
        request = AIRequest(
            messages=messages,
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            stream=True,
            extra_params=kwargs
        )
        
        try:
            
            # 准备请求数据
            request_data = self._prepare_request_data(request)
            
            # 发送流式请求
            start_time = time.time()
            
            response = self.session.post(
                self.model_config.endpoint,
                json=request_data,
                timeout=self.model_config.timeout,
                stream=True
            )
            
            
            # 检查HTTP状态
            if not response.ok:
                console.print(f"[bold red][DEBUG][/bold red] 错误响应内容: {response.text[:500]}...")
                raise Exception(f"HTTP请求失败: {response.status_code} - {response.text}")
            
            chunk_count = 0
            provider = str(getattr(self.model_config, 'provider', ''))
            
            # 处理流式响应
            for line in response.iter_lines():
                if line:
                    line_text = line.decode('utf-8')
                    
                    if line_text.startswith('data: '):
                        data_text = line_text[6:]
                        
                        if data_text.strip() == '[DONE]':
                            break
                        
                        try:
                            data = json.loads(data_text)
                            content = self._extract_stream_content(data)
                            if content:
                                chunk_count += 1
                                if callback:
                                    callback(content)
                                yield content
                        except json.JSONDecodeError:
                            console.print(f"[bold yellow][DEBUG][/bold yellow] 跳过无效的JSON数据: {data_text[:100]}...")
                            continue
            # 流式结束后输出统计信息
            if chunk_count == 0:
                try:
                    console.print(f"[bold yellow][DEBUG][/bold yellow] 流式未收到任何chunk，provider={provider}，headers={dict(response.headers)}")
                except Exception:
                    console.print(f"[bold yellow][DEBUG][/bold yellow] 流式未收到任何chunk，provider={provider}")
            else:
                console.print(f"[bold green][DEBUG][/bold green] 流式完成，收到chunks: {chunk_count}")
            
        except requests.exceptions.Timeout:
            console.print(f"[bold red][DEBUG][/bold red] 流式请求超时异常")
            raise Exception(f"请求超时 ({self.model_config.timeout}秒)")
        except requests.exceptions.ConnectionError:
            console.print(f"[bold red][DEBUG][/bold red] 流式请求连接错误异常")
            raise Exception("连接错误，请检查网络和端点地址")
        except Exception as e:
            console.print(f"[bold red][DEBUG][/bold red] 流式请求异常: {type(e).__name__}: {e}")
            raise Exception(f"流式请求失败: {e}")
    
    def _extract_stream_content(self, data: Dict[str, Any]) -> str:
        """从流式数据中提取内容

        注意：之前使用 self.model_name 进行提供商判断，当传入的是具体模型标识
        （例如 `gpt-3.5-turbo` 或 `claude-3-sonnet-20240229`）时，将导致判断失败，
        进而无法解析流式文本。这里改为优先使用配置中的 provider/name 进行判断，
        并增加更健壮的事件解析逻辑。
        """
        # 更稳健的提供商识别：优先使用配置中的 provider；其次使用 name；最后回退到 model_name
        provider_source = None
        try:
            provider_source = getattr(self.model_config, 'provider', None)
        except Exception:
            provider_source = None
        provider = (provider_source or getattr(self.model_config, 'name', None) or self.model_name or '').lower()

        # OpenAI 兼容：choices[0].delta.content
        if 'openai' in provider:
            choices = data.get('choices', [])
            if choices:
                delta = choices[0].get('delta') or {}
                # 兼容某些实现将文本放在 text 字段
                return delta.get('content') or delta.get('text') or ''

        # Anthropic / Claude SSE：content_block_delta + text_delta
        if 'claude' in provider or 'anthropic' in provider:
            event_type = data.get('type') or data.get('event')
            if event_type == 'content_block_delta':
                delta = data.get('delta', {})
                # 期望 { type: 'text_delta', text: '...' }
                if isinstance(delta, dict):
                    return delta.get('text', '')
            # 兼容一些返回只含有 delta.text 的情况
            delta = data.get('delta', {})
            if isinstance(delta, dict) and delta.get('text'):
                return delta.get('text', '')
            # 兜底：有时直接给出 content/text
            if isinstance(data.get('content'), str):
                return data.get('content')
            if isinstance(data.get('text'), str):
                return data.get('text')

        # Qwen 等其他模型：尝试多种可能格式
        if 'qwen' in provider:
            # 处理qwen模型的流式响应格式
            # 尝试多种可能的格式
            
            # 格式1: choices[0].delta.content (类似OpenAI)
            choices = data.get('choices', [])
            if choices:
                delta = choices[0].get('delta', {})
                content = delta.get('content', '')
                if content:
                    return content
            
            # 格式2: 直接的content字段
            content = data.get('content', '')
            if content:
                return content
            
            # 格式3: text字段
            content = data.get('text', '')
            if content:
                return content
            
            # 格式4: output字段
            content = data.get('output', '')
            if content:
                return content
        # 通用兜底：尝试常见字段
        for key in ('choices', 'content', 'text', 'output'):
            if key == 'choices':
                choices = data.get('choices', [])
                if choices:
                    delta = choices[0].get('delta', {})
                    content = delta.get('content') or delta.get('text')
                    if content:
                        return content
            else:
                content = data.get(key)
                if isinstance(content, str) and content:
                    return content

        return ''
    
    def switch_model(self, model_name: str):
        """
        切换模型
        
        Args:
            model_name: 新的模型名称
        """
        self.model_name = model_name
        self.model_config = self.config_manager.get_model_config(model_name)
        
        # 重新设置认证
        self.session.headers.clear()
        if self.model_config.headers:
            self.session.headers.update(self.model_config.headers)
        self._setup_auth()
    
    def get_available_models(self) -> list:
        """获取可用的模型列表"""
        return self.config_manager.list_models()
    
    def get_current_model(self) -> str:
        """获取当前使用的模型名称"""
        return self.model_name
    
    # ==================== 异步方法 ====================
    
    async def _parse_async_response(self, response_data: Dict[str, Any]) -> AIResponse:
        """异步解析响应数据"""
        return self._parse_response_data(response_data)
    
    def _parse_response_data(self, data: Dict[str, Any]) -> AIResponse:
        """解析响应数据（从字典而不是requests.Response）"""
        # 根据提供商类型解析响应
        provider = self.model_config.provider.lower()
        
        if provider == 'openai':
            return self._parse_openai_response(data)
        elif provider == 'claude':
            return self._parse_claude_response(data)
        else:
            return self._parse_generic_response(data)
    
    async def send_request_async(self, 
                               request: AIRequest, 
                               validator: ResponseValidator = None,
                               callback: Callable[[AIResponse], Any] = None) -> AIResponse:
        """
        异步发送AI请求
        
        Args:
            request: AI请求对象
            validator: 响应验证器
            callback: 响应回调函数
            
        Returns:
            AIResponse: AI响应对象
        """
        
        try:
            # 准备请求数据
            request_data = self._prepare_request_data(request)
            
            # 准备请求头
            headers = dict(self.session.headers)
            
            # 使用aiohttp进行异步请求
            timeout = aiohttp.ClientTimeout(total=self.model_config.timeout)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(
                    self.model_config.endpoint,
                    json=request_data,
                    headers=headers
                ) as response:
                    
                    # 检查HTTP状态
                    if response.status != 200:
                        error_text = await response.text()
                        console.print(f"[bold red][DEBUG][/bold red] HTTP请求失败: {response.status}")
                        console.print(f"[bold red][DEBUG][/bold red] 错误响应内容: {error_text[:500]}...")
                        raise Exception(f"HTTP请求失败: {response.status} - {error_text}")
                    
                    # 解析响应
                    response_data = await response.json()
                    ai_response = self._parse_response_data(response_data)
                    
                    # 验证响应
                    if validator:
                        is_valid, errors = validator.validate(ai_response.raw_response)
                        if not is_valid:
                            raise Exception(f"响应验证失败: {'; '.join(errors)}")
                    
                    # 执行回调
                    if callback:
                        callback(ai_response)
                    
                    return ai_response
                    
        except asyncio.TimeoutError:
            raise Exception(f"请求超时 ({self.model_config.timeout}秒)")
        except aiohttp.ClientError as e:
            raise Exception(f"连接错误: {e}")
        except Exception as e:
            console.print(f"[bold red][DEBUG][/bold red] 异步请求异常: {type(e).__name__}: {e}")
            raise
    
    async def chat_async(self, 
                        messages: Union[str, list], 
                        model: str = None,
                        max_tokens: int = None,
                        temperature: float = None,
                        validator: ResponseValidator = None,
                        callback: Callable[[AIResponse], Any] = None,
                        **kwargs) -> AIResponse:
        """
        异步聊天请求
        
        Args:
            messages: 消息内容，可以是字符串或消息列表
            model: 模型名称，如果不指定则使用默认模型
            max_tokens: 最大token数
            temperature: 温度参数
            validator: 响应验证器
            callback: 响应回调函数
            **kwargs: 其他参数
            
        Returns:
            AIResponse: AI响应对象
        """
        
        # 处理消息格式
        if isinstance(messages, str):
            messages = [{"role": "user", "content": messages}]
        
        # 添加系统提示
        if self.system_prompt:
            messages = [{"role": "system", "content": self.system_prompt}] + messages
        
        # 创建请求对象
        request = AIRequest(
            messages=messages,
            model=model or self.model_name,
            max_tokens=max_tokens,
            temperature=temperature,
            extra_params=kwargs
        )
        
        return await self.send_request_async(request, validator, callback)
    
    async def chat_with_tools_async(self, 
                                  messages: Union[str, list], 
                                  tools: List[Dict[str, Any]] = None,
                                  tool_choice: Union[str, Dict[str, Any]] = None,
                                  model: str = None,
                                  max_tokens: int = None,
                                  temperature: float = None,
                                  validator: ResponseValidator = None,
                                  callback: Callable[[AIResponse], Any] = None,
                                  **kwargs) -> AIResponse:
        """
        异步带工具的聊天请求
        
        Args:
            messages: 消息内容，可以是字符串或消息列表
            tools: 工具定义列表
            tool_choice: 工具选择策略
            model: 模型名称，如果不指定则使用默认模型
            max_tokens: 最大token数
            temperature: 温度参数
            validator: 响应验证器
            callback: 响应回调函数
            **kwargs: 其他参数
            
        Returns:
            AIResponse: AI响应对象
        """
        
        # 处理消息格式
        if isinstance(messages, str):
            messages = [{"role": "user", "content": messages}]
        
        # 添加系统提示
        if self.system_prompt:
            messages = [{"role": "system", "content": self.system_prompt}] + messages
        
        # 创建请求对象
        request = AIRequest(
            messages=messages,
            model=model or self.model_name,
            max_tokens=max_tokens,
            temperature=temperature,
            tools=tools,
            tool_choice=tool_choice,
            extra_params=kwargs
        )
        
        return await self.send_request_async(request, validator, callback)