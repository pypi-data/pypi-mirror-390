# 天翼云CLI工具

基于终端的天翼云API操作平台，提供完整的云资源管理功能。

## 📊 项目规模

- **代码量**: 13,516 行 Python 代码
- **文件数**: 23 个核心模块
- **文档**: 1,754 行完整文档
- **模块**: 5 大核心服务模块

## 功能特性

- 🔐 **安全认证**: 基于AK/SK的EOP签名认证机制，支持环境变量配置
- 🖥️ **ECS管理**: 云服务器、镜像、资源池等完整生命周期管理
- 🛡️ **安全卫士**: 漏洞扫描、客户端管理、安全策略配置
- 📊 **监控服务**: 20+ 监控API，覆盖指标查询、告警管理、事件追踪
- 💰 **计费查询**: 账单、消费明细、余额查询等财务管理
- 📝 **配置管理**: 灵活的配置文件和环境变量支持

## 项目结构

```
ctyun_cli/
├── src/
│   ├── auth/           # 认证模块 (EOP签名、传统签名)
│   ├── ecs/            # 云服务器管理 (1,068行)
│   ├── monitor/        # 监控服务 (6,057行 - 最大模块)
│   ├── security/       # 安全卫士 (1,439行)
│   ├── billing/        # 计费查询 (1,913行)
│   ├── cli/            # 命令行界面 (1,488行)
│   ├── config/         # 配置管理
│   ├── client.py       # 核心API客户端
│   └── utils/          # 工具函数
├── tests/              # 测试文件
├── docs/               # 文档
│   ├── usage.md        # 使用指南
│   ├── overview.md     # 项目概述
│   └── security-guide.md  # 安全指南
├── MONITOR_USAGE.md    # 监控服务使用文档
├── requirements.txt    # Python依赖
└── README.md          # 项目说明
```

## 快速开始

### 安装依赖
```bash
cd ctyun_cli
pip install -r requirements.txt
```

### 配置认证（推荐使用环境变量）
```bash
# 方式1: 环境变量（推荐，更安全）
export CTYUN_ACCESS_KEY=your_access_key
export CTYUN_SECRET_KEY=your_secret_key

# 方式2: 交互式配置
python setup_config.py

# 方式3: 命令行配置
ctyun-cli configure --access-key YOUR_AK --secret-key YOUR_SK --region cn-north-1
```

### 使用CLI
```bash
# 查看帮助
ctyun-cli --help

# 显示配置
ctyun-cli show-config

# 云服务器管理
ctyun-cli ecs list                    # 列出实例
ctyun-cli ecs regions                 # 查询资源池
ctyun-cli ecs create --name "test"    # 创建实例

# 监控服务（20+ API）
ctyun-cli monitor query-data --region-id <id> --metric CPUUtilization
ctyun-cli monitor query-alert-history --region-id <id>
ctyun-cli monitor query-alarm-rules --region-id <id> --service ctecs

# 安全卫士
ctyun-cli security agents             # 客户端列表
ctyun-cli security scan-result        # 扫描结果

# 计费查询
ctyun-cli billing balance             # 查询余额
ctyun-cli billing bills --month 202411  # 月度账单
```

## 技术栈

- **语言**: Python 3.8+
- **CLI框架**: Click
- **HTTP客户端**: requests
- **认证机制**: 
  - 天翼云EOP签名认证（HMAC-SHA256）
  - 传统AK/SK签名
- **配置管理**: INI配置文件 + 环境变量
- **测试框架**: pytest

## 核心特性

### 🔒 安全性
- ✅ 支持环境变量配置（避免硬编码密钥）
- ✅ EOP签名认证（安全卫士、监控服务）
- ✅ 传统签名认证（ECS、计费服务）
- ✅ 所有测试文件已移除硬编码AK/SK

### 📊 监控服务（最大模块 - 6,057行）
- 20+ 监控API完整覆盖
- 指标查询、告警管理、事件追踪
- Top-N查询（CPU、内存、维度、资源、指标、事件）
- 自定义监控、告警规则、联系人管理
- 详见 [MONITOR_USAGE.md](MONITOR_USAGE.md)

### 🛡️ 安全卫士
- 漏洞扫描结果查询
- 客户端管理
- 专用EOP签名认证

### 💰 计费查询
- 账户余额、账单查询
- 消费明细、账户流水
- 月度消费统计

## 文档

- [使用指南](docs/usage.md) - 详细的使用说明
- [监控服务文档](MONITOR_USAGE.md) - 20+ 监控API使用指南
- [项目概述](docs/overview.md) - 架构设计说明
- [安全指南](docs/security-guide.md) - 安全最佳实践
- [开发指南](AGENTS.md) - 开发者参考