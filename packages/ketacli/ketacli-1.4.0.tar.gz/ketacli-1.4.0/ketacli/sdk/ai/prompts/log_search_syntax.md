# SPL 日志查询语法（LLM 精确写作版）

本文档专为“日志类仓库”的 SPL 编写而设计，目标是让模型稳定生成可执行且正确的查询。指标/资源类仓库请参考 `metric_search_syntax.md`。

## 核心原则（必须遵守）

- 使用 `search2` 引擎；所有查询以 `search2` 开头。
- 时间参数必须紧跟在 `search2` 之后，且位于 `repo` 之前：`search2 start="..." end="..." repo="..."`。
- 必须包含 `repo` 参数；可用 `repo="*"` 进行多仓库搜索，但更推荐明确仓库名。
- 字段名用单引号包裹，字段值用双引号包裹；值内若包含双引号，用三双引号包裹（`"""..."""`）。
- 统计函数必须包含括号：`stats count() as 'cnt'`；禁止 `stats count as 'cnt'`。
- 排序必须使用 `sort by`：`sort by 'response_time' desc`；禁止 `sort 'response_time' desc`、`sort -'response_time'`。
- 复杂条件使用括号明确优先级：`(cond1 AND cond2) OR cond3`。
- 通过管道 `|` 串联命令；每个命令的参数与顺序遵循下文规范模板。

## 规范模板（黄金模板）

```spl
# 通用结构
search2 start="-24h" end="@h" repo="<仓库名>" <过滤条件>
| fields '<字段1>', '<字段2>'
| eval '<新字段>' = <表达式>
| stats <函数()> as '<别名>' by '<分组1>', '<分组2>'
| sort by '<排序字段>' desc
| limit 50
```

示例（错误分析）：
```spl
search2 start="-24h" repo="web_logs" 'status'>=400 AND 'host'="web01"
| stats count() as 'cnt' by 'status', 'url'
| sort by 'cnt' desc
```

## 参数与语法细则

### 1) 时间参数（start/end）
- 位置：必须紧跟 `search2`，在 `repo` 之前。
- 相对时间示例：
  - `start="-1h"`（近 1 小时）
  - `start="-d@d" end="@d"`（昨天整天，不包含今天）
  - `start="-3d"`（近 3 天）
  - `start="-M@M" end="@M"`（上个月）
- 对齐符号：`@s @m @h @d @w @M @y`。

### 2) 仓库参数（repo）
- 必填：`repo="仓库名"`。
- 多仓库：`repo="*"`（尽量避免，推荐明确仓库）。

### 3) 过滤条件（WHERE 子句）
- 引用规则：`'字段名'="值"`，数值或比较时字段仍需单引号：`'status'>=400`。
- 合并条件：`AND`/`OR`，使用括号确保优先级。
- 全文搜索（强烈建议）：无需写字段名，直接写字符串或通配符作为全文匹配：
  - `"error"`、`"warning"`、`"*Forbidden*"`。
  - 说明：日志查询对原始文本进行匹配（内部为 `_raw`），不需要也不推荐写显式字段名。
  - 禁止使用 `contains`/`like` 等非日志语法的运算符。
- 集合判断：`in ("WARN","ERROR")`。

### 4) 管道命令（按常用顺序）
- `fields`：选择或排除字段
  - `| fields 'timestamp', 'user', 'action'`
  - `| fields - '_raw', '_time'`
- `rename`：重命名字段
  - `| rename 'user' as 'username'`
- `eval`：计算字段
  - `| eval 'response_sec' = 'response_time' / 1000`
  - `| eval 'status_desc' = if('status'>=200 AND 'status'<300, "Success", "Error")`
  - `| eval 'status_desc' = case('status'>=200 AND 'status'<300, "Success", 'status'>=400, "Error", 1=1, "Other")`
- `stats`：聚合统计（函数需带括号）
  - `| stats count() as 'cnt' by 'status'`
  - `| stats avg('response_time'), max('response_time') by 'host'`
- `timechart`：时序分析
  - `| timechart span="5m" count() as 'requests'`
  - `| timechart span="1h" avg('cpu_usage') by 'host', '_time'`
- 排序与限制
  - `| sort by 'response_time' asc`
  - `| limit 10`
  - `| dedup 'user'`
  - `| top 10 'url'`
- 其它常用
  - `| rex field='_raw' "(?<method>\w+)\s+(?<url>\S+)"`
  - `| convert num('response_time')`

### 5) 常用函数速查
- 统计：`count(), sum(), avg(), min(), max(), distinct(), percentile(), earliest(), latest()`
- 字符串：`len(str), substr(str, start, length), replace(str, old, new), match(str, regex)`
- 数学：`round(num, decimals), ceil(num), floor(num), abs(num)`
- 时间：`toReadableTime(time, format), toTimestamp(X, TIMEFORMAT, ZoneOffset), now()`
- 条件：`if(cond, a, b), case(cond1, v1, cond2, v2, default), isnull(field), isnotnull(field)`

## 常见错误与修正（强约束）

- 错误：`search2 'repo'="logs" start="-3d" 'status'=500`
  - 说明：时间参数位置错误。
  - 修正：`search2 start="-3d" repo="logs" 'status'=500`。
- 错误：`stats count as 'cnt'`
  - 说明：统计函数缺少括号。
  - 修正：`stats count() as 'cnt'`。
- 错误：`sort 'response_time' desc` 或 `sort -'response_time'`
  - 说明：排序缺少 `by`。
  - 修正：`sort by 'response_time' desc`。
- 错误：字段名使用双引号或不加引号：`"status"=500`、`status=500`
  - 说明：日志语法要求字段名单引号。
  - 修正：`'status'=500`。
- 错误：未填写 `repo`
  - 说明：查询必须指定仓库。
  - 修正：`repo="<仓库名>"`。

### 全文检索误用示例（重点强调）
- 错误：`'message' contains "forbidden"`
  - 说明：日志查询语法不支持 `contains`，且全文检索无需字段名。
  - 修正：在过滤条件中直接写：`"forbidden"` 或带通配符 `"*forbidden*"`。
- 错误：`'message' like "*forbidden*"`
  - 说明：`like` 不是日志查询语法；也不需要显式字段名。
  - 修正：使用全文匹配：`"*forbidden*"`。
- 推荐写法：
  - 仅全文检索：`search2 start="-6h" end="@h" repo="logs_keta" "*Forbidden*"`
  - 结合结构化条件：`search2 start="-6h" end="@h" repo="logs_keta" 'level'="WARN" "*Forbidden*"`

## 实用示例模板

### 错误分析
```spl
search2 start="-24h" repo="web_logs" 'status'>=400 
| stats count() as 'cnt' by 'status', 'url'
| sort by 'cnt' desc
```

### 访问趋势
```spl
search2 start="-24h" repo="web_logs"
| timechart span="1h" count() as 'cnt' by 'status'
```

### 慢请求分析
```spl
search2 repo="performance_logs" 'response_time'>1000
| stats avg('response_time') as 'avg_response_time', count() as 'cnt' by 'url'
| sort by 'avg_response_time' desc
```

### 异常检测
```spl
search2 repo="api_logs"
| timechart span="5m" avg('response_time') as 'avg_time'
| eventstats avg('avg_time') as 'overall_avg', stdev('avg_time') as 'stdev'
| eval 'upper_bound' = 'overall_avg' + 2 * 'stdev'
| where 'avg_time' > 'upper_bound'
```

### 用户活跃度
```spl
search2 start="-7d" repo="user_logs" 
| stats count() as 'actions', dc('session_id') as 'sessions' by 'user'
| eval 'avg_actions_per_session' = 'actions'/'sessions'
| sort by 'avg_actions_per_session' desc
```

## 生成检查清单（在输出前自检）

- 是否以 `search2` 开头？
- 是否将 `start`/`end` 紧跟 `search2` 并置于 `repo` 前？
- 是否包含 `repo="..."`？
- 是否为日志语法使用单引号包裹字段名、双引号包裹值？
- 是否在统计函数中使用了括号（如 `count()`）？
- 是否在排序中使用了 `sort by`？
- 是否为复杂条件添加了括号明确优先级？
- 是否合理使用了 `fields`、`limit` 来控制输出？
- 是否避免了不必要的全量扫描与过大时间范围？
- 是否可以通过 `| limit 1` 快速验证字段与样例数据？

## 调试与优化建议

1. 先用 `| limit 1` 查看字段与样例值，再逐步增加条件。
2. 复杂查询分段执行：先过滤，再统计，再排序与限制。
3. 无结果时优先调整时间范围与匹配策略：扩大 `start`，使用模糊匹配（如包含通配符），减少过严过滤条件。

## 搜索示例
```spl
search2 start = "-1d@d" repo="_internal" AND origin = "_collector" AND repoName | eval countDate=toReadableTime(_time, "yyyy-MM-dd") | stats sum(kiloBytesProcessed) as 'dailyIncrease' by repoName,countDate | where countDate = "2025-10-15"
search2 repo="_internal" AND origin = "_collector" | eval eventsNumPS = eventsNum / 30,failDocNum = failDocNum / 30,succDocNum = succDocNum / 30 | timechart span="30s" sum(eventsNumPS) as '总数',sum(failDocNum) as '失败数',sum(succDocNum) as '成功数' | sort by _time asc
```spl
search2 repo="_internal" AND origin = "_collector" | eval kiloBytesPS=kiloBytes/30 | timechart span="30s" sum(kiloBytesPS) as '流量' | sort by _time asc
search2 repo="_internal" AND origin="_collector"| timechart span="30s" avg(avgHandlingTimeInMilli) as '响应时间'| sort by _time asc
```spl
search2 repo="_internal" AND origin = "_collector"| where in(host, "keta-web-10-0-1-154","keta-web-10-0-1-225")| eval eventsNumPS=eventsNum/30| timechart span="30s" sum(eventsNumPS) as eps by host| sort by _time asc
```spl
search2 repo="_internal" AND origin = "_collector"| where in(repoName, "app_docker_log_tel")| eval eventsNumPS=eventsNum/30| timechart span="30s" sum(eventsNumPS) as eps by repoName| sort by _time asc
```spl
search2 repo="infrastructure_monitoring_metrics" AND (infra_type="kubernetes" OR service="kubernetes") AND name="pod_container" AND origin="kubernetes_cluster"| stats count() as c by kube_cluster_name,pod_name,namespace| stats count() as num by kube_cluster_name,namespace| sort 10 by num desc
```spl
search2 repo="infrastructure_monitoring_metrics" AND (infra_type="kubernetes" OR service="kubernetes") AND rigin="kubernetes_cluster"
| stats count() as c by kube_cluster_name,namespace| fields - c| stats count() as c
```