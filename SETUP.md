# Budget Travel China Skill - 环境配置指南

本文档说明如何安装和配置 Budget Travel China skill 所需的依赖环境。

---

## 📦 必需依赖

### 1. icalBuddy（日历管理）

**用途**：读取和管理 Apple Calendar 事件，用于记忆系统（存储旅行日程）

#### macOS 安装

```bash
brew install ical-buddy
```

#### 授权

首次运行时，macOS 会请求访问日历权限：

1. 运行任意 icalBuddy 命令（如 `icalBuddy eventsToday`）
2. 系统弹窗：允许 "Terminal" 访问 "日历"
3. 点击 **"好"** / **"OK"**

**手动授权**（如果没弹窗）：
- 系统设置 → 隐私与安全性 → 日历
- 勾选 **Terminal**（或你的终端 App）

#### 验证安装

```bash
icalBuddy --version
# 输出：1.10.1

icalBuddy eventsToday
# 输出：今天的日历事件（如果没有则为空）
```

#### 其他平台

- **Linux**：不支持（icalBuddy 是 macOS 专用工具）
  - 替代方案：使用 Google Calendar API 或其他日历服务
- **Windows**：不支持
  - 替代方案：WSL2 + Google Calendar API

---

### 2. mcporter（MCP 客户端，用于 Exa 搜索）

**用途**：调用 Exa web 搜索引擎（免费，无需 API key）

#### 安装

```bash
npm install -g @openclaw/mcporter
```

#### 配置 Exa server

```bash
mcporter config add exa sse+https://exa.mcpservers.org/sse
```

#### 验证安装

```bash
mcporter list
# 应显示：exa (2 tools, X.Xs)

mcporter call 'exa.web_search_exa(query: "test", numResults: 1)'
# 应返回搜索结果
```

---

### 3. Python 依赖（可选）

**用途**：部分脚本使用 Python（如未来的高德 API 集成）

#### 安装

```bash
# macOS/Linux
python3 --version  # 确认 Python 3.7+

# 如无 Python，macOS 用户：
brew install python3
```

#### Python 库（按需安装）

```bash
# 高德 API 支持（可选，目前已改用 Exa）
pip3 install requests
```

---

## 🔧 可选依赖

### 1. 小红书 MCP Server（增强共享单车检测）

**用途**：实地用户反馈，交叉验证共享单车信息

#### 安装（Docker 方式，推荐）

```bash
docker run -d \
  --name xiaohongshu-mcp \
  -p 18060:18060 \
  --platform linux/amd64 \
  xpzouying/xiaohongshu-mcp

mcporter config add xiaohongshu http://localhost:18060/mcp
```

#### 验证

```bash
mcporter list
# 应显示：xiaohongshu (X tools, X.Xs)
```

**注意**：小红书 MCP 需要登录才能使用完整功能，详见 `~/.openclaw/skills/xiaohongshu-skills/SKILL.md`

---

### 2. 高德地图 API（已弃用，改用 Exa）

~~**用途**：实时查询共享单车（已被 Exa 替代）~~

如果你仍想使用高德 API：

1. 申请 API key：https://console.amap.com/dev/key/app
2. 配置环境变量：
   ```bash
   echo 'export AMAP_API_KEY="your_key_here"' >> ~/.zshrc
   source ~/.zshrc
   ```

---

## 🧪 测试配置

运行以下命令确认环境配置正确：

```bash
cd ~/.openclaw/my-skills/budget-travel

# 测试共享单车检测（Exa + 小红书交叉验证）
python3 scripts/check_bike_sharing.py 苏州

# 测试火车查询
python3 scripts/search_trains.py 北京 上海

# 测试日历（验证 icalBuddy 授权）
icalBuddy eventsToday
```

**预期输出**：
- ✅ 共享单车检测报告（包含 Exa 和小红书数据）
- ✅ 火车票查询链接
- ✅ 今日日历事件（或空）

---

## 🚨 常见问题

### Q1: icalBuddy 命令卡住不动

**原因**：未授权日历访问  
**解决**：
1. 按 `Ctrl+C` 终止命令
2. 系统设置 → 隐私与安全性 → 日历 → 勾选 Terminal
3. 重新运行命令

### Q2: mcporter 找不到 exa

**原因**：未配置 Exa server  
**解决**：
```bash
mcporter config add exa sse+https://exa.mcpservers.org/sse
mcporter list  # 确认 exa 在列表中
```

### Q3: 小红书 MCP 连接失败

**原因**：Docker 容器未启动  
**解决**：
```bash
docker ps | grep xiaohongshu  # 检查容器状态
docker start xiaohongshu-mcp  # 如果未运行
```

### Q4: Python 脚本报错 "No module named 'requests'"

**原因**：未安装 requests 库  
**解决**：
```bash
pip3 install requests
```

---

## 📚 相关文档

- **icalBuddy 官方文档**: https://github.com/DavidKaluta/icalBuddy
- **mcporter 文档**: https://github.com/modelcontextprotocol/servers
- **Exa 搜索文档**: https://docs.exa.ai/
- **小红书 MCP**: `~/.openclaw/skills/xiaohongshu-skills/SKILL.md`

---

## 🔄 版本兼容性

| 工具 | 最低版本 | 测试版本 | 平台 |
|------|---------|---------|------|
| icalBuddy | 1.8.0 | 1.10.1 | macOS only |
| mcporter | 0.5.0 | 0.7.3 | macOS / Linux |
| Python | 3.7 | 3.11 | 跨平台 |
| Docker | 20.10 | 27.x | 跨平台（小红书 MCP） |

---

**最后更新**：2026-03-14  
**维护者**：虾老弟 🦐

有问题欢迎提 issue: https://github.com/hananikaze/budget-travel/issues
