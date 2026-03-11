# 共享单车数据 API 配置说明

## 概述

Budget Travel China skill 支持两种共享单车检测方式：
1. **静态数据库**（默认）：`scripts/check_bike_sharing.py`
2. **实时 API 查询**（可选）：`scripts/check_bike_realtime.py`

---

## 方案对比

| 特性 | 静态数据库 | 实时 API 查询 |
|------|-----------|--------------|
| **准确性** | 中等（需手动更新） | 高（实时数据） |
| **覆盖城市** | 50+ 常见城市 | 全国所有城市 |
| **API 依赖** | ❌ 无需 API key | ✅ 需要高德地图 API key |
| **网络要求** | ❌ 无 | ✅ 需要联网 |
| **查询速度** | 极快（< 0.1s） | 较快（1-3s） |
| **成本** | 免费 | 免费（有配额限制） |
| **推荐场景** | 常见旅游城市 | 冷门/小城市 |

---

## 方案 1：静态数据库（默认）

### 使用方法
```bash
python3 scripts/check_bike_sharing.py 城市名
```

### 优点
- 无需配置
- 离线可用
- 覆盖常见旅游城市

### 缺点
- 数据可能过期（共享单车政策变化快）
- 冷门城市可能未收录

### 数据来源
- 小红书旅游攻略
- 马蜂窝游记
- 用户反馈
- 手动实地验证

### 更新频率
- 季度更新（每 3 个月）
- 用户可通过 GitHub 提交更新

---

## 方案 2：实时 API 查询（推荐）

### 配置步骤

#### 1. 申请高德地图 API key（免费）

1. 访问 [高德开放平台](https://console.amap.com/dev/key/app)
2. 注册/登录账号
3. 创建应用：
   - 应用名称：`Budget Travel China` 或任意
   - 应用类型：`Web 服务`
4. 添加 Key：
   - Key 名称：`Bike Sharing Checker`
   - 服务平台：`Web 服务`
5. 复制生成的 API Key

#### 2. 配置环境变量

**临时配置**（当前终端有效）：
```bash
export AMAP_API_KEY="你的API_Key"
```

**永久配置**（推荐）：

**macOS/Linux (Zsh)**:
```bash
echo 'export AMAP_API_KEY="你的API_Key"' >> ~/.zshrc
source ~/.zshrc
```

**macOS/Linux (Bash)**:
```bash
echo 'export AMAP_API_KEY="你的API_Key"' >> ~/.bashrc
source ~/.bashrc
```

**验证配置**：
```bash
echo $AMAP_API_KEY  # 应输出你的 API Key
```

#### 3. 安装依赖
```bash
pip3 install requests
```

#### 4. 使用实时查询
```bash
python3 scripts/check_bike_realtime.py 城市名
```

**示例**：
```bash
python3 scripts/check_bike_realtime.py 拉萨
```

**输出**：
```
🔍 正在查询 拉萨 的共享单车情况...

==================================================
城市：拉萨
==================================================

❌ 未检测到御三家共享单车

   可能原因：
   1. 该城市确实没有企业共享单车
   2. 有地方政府公共自行车（需查询当地系统）
   3. API 数据未及时更新

💡 备选方案：
   - 查询地方公共自行车系统（如杭州小红车）
   - 使用公交卡
   - 询问青旅是否有自行车租赁
==================================================
```

---

## API 配额说明

### 高德地图 Web 服务 API（免费版）

- **日调用量**：3,000 次/天
- **并发量**：30 次/秒
- **成本**：免费（个人使用足够）

### 配额管理建议

1. **启用缓存**：
   - `check_bike_realtime.py` 自动缓存结果
   - 缓存有效期：7 天
   - 缓存文件：`references/bike_cache.json`

2. **避免重复查询**：
   - 同一城市 7 天内只查一次
   - 清除缓存：`rm references/bike_cache.json`

3. **批量查询**：
   - 如需查询多个城市，建议间隔 1 秒（避免触发限流）

---

## 故障排查

### 问题 1：`❌ 未找到高德地图 API key`

**原因**：环境变量未配置  
**解决**：
```bash
export AMAP_API_KEY="你的API_Key"
# 或写入 ~/.zshrc / ~/.bashrc
```

### 问题 2：`⚠️ 网络请求失败`

**可能原因**：
1. 网络连接问题 → 检查网络
2. API key 错误 → 重新检查 key
3. API 配额用完 → 等待次日刷新

**验证 API key**：
```bash
curl "https://restapi.amap.com/v3/ip?key=你的API_Key"
```

### 问题 3：查询结果不准确

**原因**：API 数据可能滞后  
**解决**：
1. 优先相信本地实测（到站后打开 APP）
2. 提交反馈更新静态数据库
3. 多个数据源交叉验证（小红书 + API）

---

## 使用建议

### 推荐流程

1. **常见城市**（北京、上海、成都等）：
   - 直接用静态数据库（快速可靠）
   
2. **冷门城市**（县级市、小城市）：
   - 用实时 API 查询（覆盖更全）
   
3. **实地验证**（最终确认）：
   - 到站后打开美团/哈啰/青桔 APP
   - 查看是否有可用车辆

### OpenClaw Skill 集成

在 `SKILL.md` 中，Agent 会：
1. 优先使用 `check_bike_realtime.py`（如果有 API key）
2. 回退到 `check_bike_sharing.py`（如果无 API key）
3. 提示用户实地验证（最终确认）

---

## 数据隐私

- 高德地图 API 仅查询 POI 数据，不涉及个人隐私
- 缓存文件仅存储城市名和单车品牌，不含位置信息
- API key 仅存储在本地环境变量，不上传

---

## 其他 API 选项（备选）

### 1. 百度地图 API
- 申请地址：https://lbsyun.baidu.com/apiconsole/key
- 配额：10,000 次/天（免费）
- 优点：配额更高
- 缺点：数据更新较慢

### 2. 腾讯地图 API
- 申请地址：https://lbs.qq.com/dev/console/application/mine
- 配额：10,000 次/天（免费）
- 优点：与微信集成
- 缺点：POI 数据不如高德全

**推荐**：优先使用高德地图（数据最全，更新最快）

---

## 贡献

如果你发现某个城市的共享单车数据不准确：

1. 提交 issue：https://github.com/你的仓库/issues
2. 提供信息：
   - 城市名
   - 实际情况（有/无，哪些品牌）
   - 验证时间
3. 我们会更新静态数据库

---

**更新时间**：2026-03-11  
**维护者**：虾老弟 🦐
