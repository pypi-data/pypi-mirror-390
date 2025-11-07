# 天翼云监控服务功能说明

## 功能概述

已实现天翼云监控服务的多个API接口，包括自定义监控、云主机资源使用率查询等功能。

## 已实现的功能

### 1. 自定义监控趋势数据查询

**CLI命令**: `ctyun-cli monitor custom-trend`

查询自定义监控项的时序指标趋势数据。

**示例**:
```bash
# 查询最近24小时数据
ctyun-cli monitor custom-trend \
    --region-id bb9fdb42056f11eda1610242ac110002 \
    --custom-item-id 64ea1664-4347-558e-9bc6-651341c2fa15

# 带维度过滤
ctyun-cli monitor custom-trend \
    --region-id bb9fdb42056f11eda1610242ac110002 \
    --custom-item-id 64ea1664-4347-558e-9bc6-651341c2fa15 \
    --dimension uuid=xxx \
    --dimension job=virtual_machine
```

### 2. 云主机CPU使用率Top-N

**CLI命令**: `ctyun-cli monitor cpu-top`

查询资源池中CPU使用率最高的云主机列表。

**示例**:
```bash
# 查询CPU使用率Top 3
ctyun-cli monitor cpu-top --region-id bb9fdb42056f11eda1610242ac110002

# 查询CPU使用率Top 10
ctyun-cli monitor cpu-top \
    --region-id bb9fdb42056f11eda1610242ac110002 \
    --number 10
```

### 3. 云主机内存使用率Top-N

**CLI命令**: `ctyun-cli monitor mem-top`

查询资源池中内存使用率最高的云主机列表。

**示例**:
```bash
# 查询内存使用率Top 3
ctyun-cli monitor mem-top --region-id bb9fdb42056f11eda1610242ac110002

# 查询内存使用率Top 10
ctyun-cli monitor mem-top \
    --region-id bb9fdb42056f11eda1610242ac110002 \
    --number 10
```

### 5. 查询服务维度及监控项

**CLI命令**: `ctyun-cli monitor query-items`

查询资源池下服务、维度、监控项信息。

**示例**:
```bash
# 查询所有服务和监控项
ctyun-cli monitor query-items --region-id bb9fdb42056f11eda1610242ac110002

# 查询指定服务（如ECS）的监控项
ctyun-cli monitor query-items \
    --region-id bb9fdb42056f11eda1610242ac110002 \
    --service ecs

# 只查询服务和维度信息，不显示监控项详情
ctyun-cli monitor query-items \
    --region-id bb9fdb42056f11eda1610242ac110002 \
    --ignore-items
```

### 6. 查询系统看板支持的服务维度

**CLI命令**: `ctyun-cli monitor query-sys-services`

查询系统看板支持的服务维度。

**示例**:
```bash
# 查询支持的服务维度
ctyun-cli monitor query-sys-services --region-id bb9fdb42056f11eda1610242ac110002
```

### 11. 查询资源分组列表

**CLI命令**: `ctyun-cli monitor query-resource-groups`

查询用户资源分组列表。

**示例**:
```bash
# 查询所有资源分组
ctyun-cli monitor query-resource-groups \
    --region-id bb9fdb42056f11eda1610242ac110002
    
# 模糊搜索分组名称
ctyun-cli monitor query-resource-groups \
    --region-id bb9fdb42056f11eda1610242ac110002 \
    --name "test"
    
# 查询指定分组ID
ctyun-cli monitor query-resource-groups \
    --region-id bb9fdb42056f11eda1610242ac110002 \
    --res-group-id 95f7f0cb-b5d7-547e-8667-3fceeab177d5
    
# 分页查询
ctyun-cli monitor query-resource-groups \
    --region-id bb9fdb42056f11eda1610242ac110002 \
    --page-no 1 \
    --page-size 5
```

## 通用参数说明

### 必需参数

- `--region-id`: 资源池ID（例如：`bb9fdb42056f11eda1610242ac110002` 表示华东1）

### 可选参数

- `--number`: 选取TOP值的数量，默认为3（适用于Top-N查询）
- `--output`: 输出格式，可选值：`table`（默认）、`json`、`yaml`

## 常用资源池ID

| 资源池名称 | Region ID |
|-----------|-----------|
| 华东1 | bb9fdb42056f11eda1610242ac110002 |
| 华北2 | 200000001852 |

更多资源池ID请参考：https://www.ctyun.cn/document/10026735/11055382

## 输出格式

### 表格格式（默认）

显示清晰的表格，包含排名、设备信息和使用率统计。

示例输出：
```
云主机CPU使用率 Top 3
================================================================================
排名    设备ID                                    设备名称         CPU使用率(%)
#1      3080069a-ca2b-fca1-f038-5e6e00dd7630     ecm-be47        56.69%
#2      0582fe3b-97bd-ac16-2b88-1c1a84fe89ce     ecm-69c1        46.70%
#3      b7862cdf-6b1b-bdfd-8410-ba71d2a7ecb8     ecm-71e7        45.03%

共找到 3 台云主机
CPU使用率统计:
  最高: 56.69%
  最低: 45.03%
  平均: 49.47%
```

### JSON格式

使用 `--output json` 参数输出完整的JSON数据。

### YAML格式

使用 `--output yaml` 参数输出YAML格式数据。

## Python SDK使用

```python
from client import CTYUNClient
from monitor.client import MonitorClient

# 初始化客户端
client = CTYUNClient(
    access_key='your_access_key',
    secret_key='your_secret_key',
    region='cn-north-1'
)

monitor_client = MonitorClient(client)

# 查询CPU使用率Top-N
result = monitor_client.query_cpu_top(
    region_id='bb9fdb42056f11eda1610242ac110002',
    number=5
)

if result['success']:
    cpu_list = result['data']['cpuList']
    for item in cpu_list:
        print(f"{item['name']}: {float(item['value'])*100:.2f}%")

# 查询内存使用率Top-N
result = monitor_client.query_mem_top(
    region_id='bb9fdb42056f11eda1610242ac110002',
    number=5
)

# 查询磁盘使用率Top-N
result = monitor_client.query_disk_top(
    region_id='bb9fdb42056f11eda1610242ac110002',
    number=5
)

# 查询自定义监控趋势数据
result = monitor_client.query_custom_item_trendmetricdata(
    region_id='bb9fdb42056f11eda1610242ac110002',
    custom_item_id='64ea1664-4347-558e-9bc6-651341c2fa15',
    start_time=1687158009,
    end_time=1687158309
)
```

## API端点

所有监控API使用统一的端点：
- **Endpoint**: `https://monitor-global.ctapi.ctyun.cn`
- **认证方式**: EOP签名认证

## 已实现的API列表

| 功能 | URI | Python方法 | CLI命令 |
|-----|-----|-----------|---------|
| 自定义监控趋势数据 | `/v4/monitor/query-custom-item-trendmetricdata` | `query_custom_item_trendmetricdata()` | `custom-trend` |
| CPU使用率Top-N | `/v4/monitor/query-cpu-top` | `query_cpu_top()` | `cpu-top` |
| 内存使用率Top-N | `/v4/monitor/query-mem-top` | `query_mem_top()` | `mem-top` |
| 磁盘使用率Top-N | `/v4/monitor/query-disk-top` | `query_disk_top()` | `disk-top` |
| 服务维度及监控项 | `/v4/monitor/query-items` | `query_monitor_items()` | `query-items` |
| 系统看板服务维度 | `/v4/monitor/monitor-board/query-sys-services` | `query_sys_services()` | `query-sys-services` |
| 监控看板详情 | `/v4/monitor/monitor-board/describe` | `describe_monitor_board()` | `describe` |
| 监控看板列表 | `/v4/monitor/monitor-board/list` | `list_monitor_boards()` | `list` |
| 监控视图详情 | `/v4/monitor/monitor-board/describe-view` | `describe_monitor_view()` | `describe-view` |
| 监控视图数据查询 | `/v4/monitor/monitor-board/query-view-data` | `query_view_data()` | `query-view-data` |
| 资源分组列表查询 | `/v4.1/monitor/query-resource-groups` | `query_resource_groups()` | `query-resource-groups` |
| 资源分组详情查询 | `/v4.1/monitor/describe-resource-group` | `describe_resource_group()` | `describe-resource-group` |
| 实时监控数据查询 | `/v4.2/monitor/query-latest-metric-data` | `query_latest_metric_data()` | `query-latest-metric-data` |
| 历史监控数据查询 | `/v4.2/monitor/query-history-metric-data` | `query_history_metric_data()` | `query-history-metric-data` |
| 事件服务维度信息查询 | `/v4/monitor/events/query-services` | `query_event_services()` | `query-event-services` |
| 事件数据统计 | `/v4/monitor/events/count-data` | `count_event_data()` | `count-event-data` |
| 事件列表查询 | `/v4/monitor/events/query-list` | `query_event_list()` | `query-event-list` |
| 事件详情查询 | `/v4/monitor/events/query-detail` | `query_event_detail()` | `query-event-detail` |
| 查询事件 | `/v4/monitor/events/query-events` | `query_events()` | `query-events` |
| 查询自定义事件 | `/v4/monitor/query-custom-events` | `query_custom_events()` | `query-custom-events` |
| 查询自定义事件监控详情 | `/v4/monitor/query-custom-event-data` | `query_custom_event_data()` | `query-custom-event-data` |
| 查看自定义事件告警规则详情 | `/v4/monitor/describe-custom-event-alarm-rule` | `describe_custom_event_alarm_rule()` | `describe-custom-event-alarm-rule` |
| 查询告警历史 | `/v4/monitor/query-alert-history` | `query_alert_history()` | `query-alert-history` |
| 查询告警历史详情 | `/v4/monitor/query-alert-history-info` | `query_alert_history_info()` | `query-alert-history-info` |

### 14. 历史监控数据查询
**CLI命令**: `ctyun-cli monitor query-history-metric-data`
查询指定时间段内的设备时序指标监控数据。
**示例**:
```bash
# 查询最近1小时的CPU使用率数据
ctyun-cli monitor query-history-metric-data \
    --region-id bb9fdb42056f11eda1610242ac110002 \
    --service ecs \
    --dimension ecs \
    --item-name-list cpu_util \
    --start-time 1665305264 \
    --end-time 1665391665 \
    --dimension-name uuid \
    --dimension-value 000f0322-1f4d-8cc8-bb2e-1c30fb751aa5
    
# 查询最近24小时的CPU和磁盘使用率数据，使用最大值聚合
ctyun-cli monitor query-history-metric-data \
    --region-id bb9fdb42056f11eda1610242ac110002 \
    --service ecs \
    --dimension ecs \
    --item-name-list cpu_util \
    --item-name-list disk_util \
    --start-time 1665305264 \
    --end-time 1665391665 \
    --fun max \
    --period 3600 \
    --dimension-name uuid \
    --dimension-value 000f0322-1f4d-8cc8-bb2e-1c30fb751aa5
```

### 15. 事件服务维度信息查询
**CLI命令**: `ctyun-cli monitor query-event-services`
获取资源池下服务维度信息（事件监控）。
**示例**:
```bash
# 查询所有事件服务维度信息
ctyun-cli monitor query-event-services \
    --region-id bb9fdb42056f11eda1610242ac110002
    
# 查询指定服务的维度信息
ctyun-cli monitor query-event-services \
    --region-id bb9fdb42056f11eda1610242ac110002 \
    --service ecs
    
# 查询事件类型的服务维度信息
ctyun-cli monitor query-event-services \
    --region-id bb9fdb42056f11eda1610242ac110002 \
    --monitor-type event
```

### 16. 事件数据统计
**CLI命令**: `ctyun-cli monitor count-event-data`
根据指定时间段统计指定事件发生情况。
**示例**:
```bash
# 统计最近1小时的迁移事件
ctyun-cli monitor count-event-data \
    --region-id bb9fdb42056f11eda1610242ac110002 \
    --event-name migration_event_start \
    --service ecs \
    --dimension ecs \
    --start-time 1647424360 \
    --end-time 1647424660 \
    --period 300
    
# 统计资源分组的事件
ctyun-cli monitor count-event-data \
    --region-id bb9fdb42056f11eda1610242ac110002 \
    --event-name migration_event_start \
    --service ecs \
    --dimension ecs \
    --start-time 1647424360 \
    --end-time 1647424660 \
    --period 300 \
    --res-group-id 9cb2b330-1dd8-5ec4-9c6d-b07fe65a9aca
```

### 17. 事件列表查询
**CLI命令**: `ctyun-cli monitor query-event-list`
根据指定时间段查询事件发生情况。
**示例**:
```bash
# 查询所有事件
ctyun-cli monitor query-event-list \
    --region-id bb9fdb42056f11eda1610242ac110002 \
    --service ecs \
    --dimension ecs \
    --start-time 1647424360 \
    --end-time 1647424660
    
# 查询指定事件
ctyun-cli monitor query-event-list \
    --region-id bb9fdb42056f11eda1610242ac110002 \
    --service ecs \
    --dimension ecs \
    --start-time 1647424360 \
    --end-time 1647424660 \
    --event-name-list migration_event_start \
    --event-name-list migration_event_complete
    
# 分页查询
ctyun-cli monitor query-event-list \
    --region-id bb9fdb42056f11eda1610242ac110002 \
    --service ecs \
    --dimension ecs \
    --start-time 1647424360 \
    --end-time 1647424660 \
    --page-no 1 \
    --page-size 10
```

### 18. 查询事件详情

**CLI命令**: `ctyun-cli monitor query-event-detail`

根据指定时间段查询事件发生情况的详细信息。

**示例**:
```bash
# 查询指定事件的详情
ctyun-cli monitor query-event-detail \
    --region-id bb9fdb42056f11eda1610242ac110002 \
    --event-name migration_event_start \
    --service ecs \
    --dimension ecs \
    --start-time 1647424360 \
    --end-time 1647424660
    
# 分页查询
ctyun-cli monitor query-event-detail \
    --region-id bb9fdb42056f11eda1610242ac110002 \
    --event-name migration_event_start \
    --service ecs \
    --dimension ecs \
    --start-time 1647424360 \
    --end-time 1647424660 \
    --page-no 1 \
    --page-size 10
    
# 查询资源分组的事件详情
ctyun-cli monitor query-event-detail \
    --region-id bb9fdb42056f11eda1610242ac110002 \
    --event-name migration_event_start \
    --service ecs \
    --dimension ecs \
    --start-time 1647424360 \
    --end-time 1647424660 \
    --res-group-id 9cb2b330-1dd8-5ec4-9c6d-b07fe65a9aca
```

### 19. 查询事件

**CLI命令**: `ctyun-cli monitor query-events`

获取资源池下指定维度下的事件列表。

**示例**:
```bash
# 查询ECS服务的事件列表
ctyun-cli monitor query-events \
    --region-id bb9fdb42056f11eda1610242ac110002 \
    --service ecs \
    --dimension ecs
```

### 20. 查询自定义事件

**CLI命令**: `ctyun-cli monitor query-custom-events`

查询自定义事件列表。

**示例**:
```bash
# 查询所有自定义事件
ctyun-cli monitor query-custom-events \
    --region-id bb9fdb42056f11eda1610242ac110002

# 根据事件名称模糊搜索
ctyun-cli monitor query-custom-events \
    --region-id bb9fdb42056f11eda1610242ac110002 \
    --name "异常"

# 查询指定ID的自定义事件
ctyun-cli monitor query-custom-events \
    --region-id bb9fdb42056f11eda1610242ac110002 \
    --custom-event-id EVENTacd8b6b4610b97d202306301808

# 分页查询
ctyun-cli monitor query-custom-events \
    --region-id bb9fdb42056f11eda1610242ac110002 \
    --page-no 1 \
    --page-size 10
```

### 21. 查询自定义事件监控详情

**CLI命令**: `ctyun-cli monitor query-custom-event-data`

查询自定义事件的监控详情。

**示例**:
```bash
# 查询所有自定义事件监控详情（默认7天内）
ctyun-cli monitor query-custom-event-data \
    --region-id bb9fdb42056f11eda1610242ac110002

# 查询指定时间范围内的事件监控详情
ctyun-cli monitor query-custom-event-data \
    --region-id bb9fdb42056f11eda1610242ac110002 \
    --start-time 1688119721 \
    --end-time 1688119736

# 查询指定事件ID的监控详情
ctyun-cli monitor query-custom-event-data \
    --region-id bb9fdb42056f11eda1610242ac110002 \
    --custom-event-id EVENTacd8b6b4610b97d202306301808

# 查询多个事件ID的监控详情
ctyun-cli monitor query-custom-event-data \
    --region-id bb9fdb42056f11eda1610242ac110002 \
    --custom-event-id EVENTacd8b6b4610b97d202306301808 \
    --custom-event-id EVENT789012345678901234567890123

# 分页查询
ctyun-cli monitor query-custom-event-data \
    --region-id bb9fdb42056f11eda1610242ac110002 \
    --page-no 1 \
    --page-size 10
```

### 22. 查看自定义事件告警规则详情

**CLI命令**: `ctyun-cli monitor describe-custom-event-alarm-rule`

查看自定义事件告警规则的详情信息。

**示例**:
```bash
# 查看告警规则详情
ctyun-cli monitor describe-custom-event-alarm-rule \
    --region-id bb9fdb42056f11eda1610242ac110002 \
    --alarm-rule-id 3dbd23b2-74e2-53f8-869c-6fe6b07b9dba
```

### 23. 查询告警历史

**CLI命令**: `ctyun-cli monitor query-alert-history`

查询告警历史，返回结果按触发时间降序排列。

**示例**:
```bash
# 查询正在告警的事件
ctyun-cli monitor query-alert-history \
    --region-id bb9fdb42056f11eda1610242ac110002 \
    --status 0

# 查询告警历史（默认最近24小时）
ctyun-cli monitor query-alert-history \
    --region-id bb9fdb42056f11eda1610242ac110002 \
    --status 1

# 查询指定时间范围的告警历史
ctyun-cli monitor query-alert-history \
    --region-id bb9fdb42056f11eda1610242ac110002 \
    --status 1 \
    --start-time 1698896251 \
    --end-time 1698982651

# 按告警规则ID精确查询
ctyun-cli monitor query-alert-history \
    --region-id bb9fdb42056f11eda1610242ac110002 \
    --status 1 \
    --search-key alarmRuleID \
    --search-value f704a846-7194-5e57-9859-3b0e91f986f4

# 按规则名称模糊查询
ctyun-cli monitor query-alert-history \
    --region-id bb9fdb42056f11eda1610242ac110002 \
    --status 1 \
    --search-key name \
    --search-value "测试"

# 按服务过滤
ctyun-cli monitor query-alert-history \
    --region-id bb9fdb42056f11eda1610242ac110002 \
    --status 1 \
    --service ecs \
    --service evs

# 分页查询
ctyun-cli monitor query-alert-history \
    --region-id bb9fdb42056f11eda1610242ac110002 \
    --status 1 \
    --page-no 1 \
    --page-size 20
```

### 24. 查询告警历史详情

**CLI命令**: `ctyun-cli monitor query-alert-history-info`

查询单条告警历史的详细信息。

**示例**:
```bash
# 查询告警历史详情
ctyun-cli monitor query-alert-history-info \
    --issue-id 65b08a5848091836a6f2afd8
```

## 错误处理

常见错误码：
- `Openapi.RegionInfo.AccessFailed`: 资源池ID不存在或无权访问
- `Monitor.DataQuery.QueryError`: 查询数据失败
- `CTAPI_10002`: 无效的AK/SK

## 测试

运行测试脚本：

```bash
cd ctyun_cli

# 测试自定义监控
python test_custom_monitor.py

# 测试CPU Top-N
python test_cpu_top.py

# 测试内存Top-N
python test_mem_top.py
```

## 功能验证状态

✅ EOP签名认证正确  
✅ API端点正确  
✅ 请求参数格式正确  
✅ 真实环境调用成功  
✅ 所有功能测试通过
✅ 实时监控数据查询功能已实现
✅ 历史监控数据查询功能已实现
