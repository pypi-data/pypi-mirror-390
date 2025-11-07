# 指标/资源查询语法（LLM 精确写作版）

本文档面向“指标/资源仓库”的 SPL 写作与生成，目标是让模型稳定生成正确的指标查询。日志类仓库请参考 `log_search_syntax.md`。

## 核心原则（必须遵守）

- 使用 `mstats` 进行指标聚合与计算；不要在指标计算中添加 `search2`。
- 指标计算无需 `repo` 参数；默认对所有相关仓库的时间序列计算。
- 时间参数必须紧跟在 `mstats` 之后：`mstats start="..." end="..." span="..." <聚合表达式> ...`。
- 字段名（标签、分组字段、别名）使用单引号，字段值使用双引号；若值包含双引号，使用三双引号包裹（`"""..."""`）。
- `stats/mstats` 中的函数必须包含括号：如 `avg('cpu_usage_idle')`，禁止省略成 `avg cpu_usage_idle`。
- `where` 不支持 `in` 操作符；使用多个条件通过 `OR` 连接：`where 'host'="h1" OR 'host'="h2"`。
- 排序必须使用 `sort by`：如 `| sort by '_value' desc`；禁止 `sort '_value' desc`。
- `by '<field>'` 用于分组；确保分组字段为标签（非数值型指标字段）。

## 数据模型要点

- `_time`：毫秒级时间戳；指标按时间序列组织。
- `<tags>...`：任意标签（字符串或数组），如 `repo`、`sourcetype`、`host`、`origin`。
- `<fields>...`：指标值（双精度浮点），例如 `cpu_usage_idle`、`disk_used`。
- `_series`：时间序列唯一标识（由指标名、标签名和值组合定义）。

## 元数据查询（show 系列）

用于探索指标与标签，所有过滤匹配值必须使用双引号：

```
show tag names [| where like(name, "%memory%")]
show tag "<name>"
show metric names [| where like(name, "%cpu%")]
show metric tags [| where like(name, "%cpu%")]
show series [| where like(series, "%memory%")]
show rest "<url>" [jsonpath="<path>"]
show sql "<sql>"
```

## 黄金模板与常用模式

### 1) 基础聚合与分组
```spl
mstats start="-2h" span="1m" avg('cpu_usage_idle') as '_value' by 'host'
| sort by '_value' desc
```

### 2) 过滤与时间偏移
```spl
mstats timeshift="-1h" avg('cpu_usage_idle' host="host_0")
```

### 3) 多指标组合与派生
```spl
mstats start="-2h" avg('disk_used')/avg('disk_total')*100 as 'disk_used_pct' by 'host'
| sort by 'disk_used_pct' desc
```

### 4) rollup（序列内聚合）
```spl
# 每小时先按序列求均值，再求全局最大
mstats start="-2h" span="1h" max(rollup(cpu_usage_idle, "avg"))

# 计数增量与速率（累计计数类指标）
mstats start="-2h" sum(rollup(span_requests_total, "increase"))
mstats start="-2h" sum(rollup(span_requests_total, "rate"))
```

### 5) 直方图百分位（hperc）
```spl
# 要求：必须有 'le' 标签且包含 '+Inf'，值为累计计数；依赖 rollup rate
mstats hperc(95, span_latency_bucket) as 'p95'
```

### 6) sumRate（全序列速率之和）
```spl
mstats sumRate(span_requests_total)
```

### 7) rate（增量变化率）
```spl
# 每秒磁盘增量变化率（按 host 分组）
mstats avg('disk_used') by 'host' | rate

# 显式写法（设置单位与输入、分组）
mstats avg('disk_used') by 'host' | rate unit="1s" 'avg(disk_used)' by 'host'

# 每小时变化率
mstats avg('disk_used') by 'host' | rate unit="1h"
```

### 8) topseries（Top N 时间序列）
```spl
# 保留平均值最高的 5 个主机时间序列
mstats start="-2h" span="10m" avg('cpu_usage_idle') by 'host' | topseries 5

# 显式字段与分组 + 排序
mstats start="-2h" span="10m" avg('cpu_usage_idle') as '_value' by 'host' | topseries type="avg" reverse=true 5 '_value' by 'host' | sort by '_value' desc
```

## 常见错误与修正（强约束）

- 错误：在指标计算中使用 `search2` 或添加 `repo` 参数。
  - 修正：改为纯 `mstats` 写法，并移除 `repo`。
- 错误：时间参数未紧跟 `mstats`，位置写到后续管道中。
  - 修正：`mstats start="..." end="..." <聚合> ...`。
- 错误：函数缺少括号，如 `avg cpu_usage_idle`。
  - 修正：`avg('cpu_usage_idle')`。
- 错误：`where` 使用 `in`：`where 'host' in ["h1","h2"]`。
  - 修正：`where 'host'="h1" OR 'host'="h2"`。
- 错误：字段名未使用单引号或误用双引号：`host="h1"`、`"host"="h1"`。
  - 修正：`'host'="h1"`。
- 错误：排序缺少 `by`：`sort '_value' desc`。
  - 修正：`sort by '_value' desc`。

## 生成检查清单（在输出前自检）

- 是否使用了 `mstats`（而非 `search2`）进行指标聚合？
- 是否将 `start`/`end`/`span` 紧跟在 `mstats` 后？
- 是否正确为字段名使用单引号、为值使用双引号？
- 是否避免在 `where` 中使用 `in`，并改用 `OR`？
- 是否为函数添加了括号（如 `avg()`、`sum()`、`hperc()`）？
- 是否在排序中使用了 `sort by`？
- 是否为分组字段使用了 `by '<tag>'`，且这些字段为标签？
- 是否可以用 `| sort by` 与 `| limit` 控制输出规模？

## 调试与优化建议

1. 先用较短的时间范围与较小 `span` 验证字段与分组，再扩展范围。
2. 对累计计数型指标（如 `*_total`），优先使用 `rollup("rate")` 或 `sumRate` 进行含义正确的分析。
3. 直方图百分位必须满足桶计数与 `le=+Inf` 要求；不足数据时扩大时间窗口。
4. 无结果或值异常时，检查分组字段是否为标签、时间参数位置是否正确、函数是否带括号。

## 搜索示例
mstats count(db_service_calls_total) as count by biz_system,servicetype| fields biz_system,servicetype| eval targettype = concat("database_", substr(servicetype, 4))
mstats count(service_requests_total) as count by service, biz_system| fields service, biz_system
mstats count(messaging_service_produce_total) as count by biz_system,servicetype,service,host,port| fields biz_system,servicetype,service,host,port| eval targettype = substr(servicetype, 11)
mstats  avg('service_requests_failed_total'  ( 'service' in("keta-web") )) as 'avg(服务请求错误数  ( service in("keta-web") ))' by 'service' | eval _time = 0 | compare timeshift="-5m" type="stats"         | where periods=1          | eval 'avg(服务请求错误数  ( service in("keta-web") ))_ratio' = 'avg(服务请求错误数  ( service in("keta-web") ))_ratio'*100        | fields _time, service, 'avg(服务请求错误数  ( service in("keta-web") ))_ratio'
mstats  avg('service_requests_failed_total'  ( 'service' in("keta-data") )) as 'avg(服务请求错误数  ( service in("keta-data") ))' by 'service' | eval _time = 0 | compare timeshift="-5m" type="stats"         | where periods=1          | eval 'avg(服务请求错误数  ( service in("keta-data") ))_ratio' = 'avg(服务请求错误数  ( service in("keta-data") ))_ratio'*100        | fields _time, service, 'avg(服务请求错误数  ( service in("keta-data") ))_ratio'
mstats  avg('service_instance_requests_failed_total'  ( 'env' in("ketaops-1xx") ) AND ( 'instance' in("ketaops-1xx/keta-web-10-0-1-47") ) AND ( 'service' in("keta-web") )) as 'avg(实例请求错误数  ( env in("ketaops-1xx") ) AND ( instance in("ketaops-1xx/keta-web-10-0-1-47") ) AND ( service in("keta-web") ))' by 'env','instance','service' | eval _time = 0 | compare timeshift="-30m" type="stats"         | where periods=1          | eval 'avg(实例请求错误数  ( env in("ketaops-1xx") ) AND ( instance in("ketaops-1xx/keta-web-10-0-1-47") ) AND ( service in("keta-web") ))_ratio' = 'avg(实例请求错误数  ( env in("ketaops-1xx") ) AND ( instance in("ketaops-1xx/keta-web-10-0-1-47") ) AND ( service in("keta-web") ))_ratio'*100        | fields _time, env, instance, service, 'avg(实例请求错误数  ( env in("ketaops-1xx") ) AND ( instance in("ketaops-1xx/keta-web-10-0-1-47") ) AND ( service in("keta-web") ))_ratio'
mstats  avg('service_instance_requests_failed_total'  ( 'env' in("ketaops-1xx") ) AND ( 'instance' in("ketaops-1xx/neuralert-api-1") ) AND ( 'service' in("neuralert-api"))) as 'avg(实例请求错误数  ( env in("ketaops-1xx") ) AND ( instance in("ketaops-1xx/neuralert-api-1") ) AND ( service in("neuralert-api") ))' by 'env','instance','service' | eval _time = 0 | compare timeshift="-30m" type="stats"         | where periods=1          | eval 'avg(实例请求错误数  ( env in("ketaops-1xx") ) AND ( instance in("ketaops-1xx/neuralert-api-1") )AND ( service in("neuralert-api") ))_ratio' = 'avg(实例请求错误数  ( env in("ketaops-1xx") ) AND ( instance in("ketaops-1xx/neuralert-api-1") ) AND ( service in("neuralert-api") ))_ratio'*100        | fields _time, env, instance, service, 'avg(实例请求错误数  ( env in("ketaops-1xx") ) AND ( instance in("ketaops-1xx/neuralert-api-1") ) AND ( service in("neuralert-api") ))_ratio'
