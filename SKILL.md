---
name: budget-travel-china
description: Budget travel planning for mainland China. Plans low-cost itineraries using trains (no flights), shared bikes, hostels, and budget-friendly food. Can RECOMMEND destinations when user has only time/budget constraints, or PLAN detailed itineraries for known destinations. Use when user asks for budget/backpacker travel plans within China, mentions limited budget, prefers trains over flights, needs cost-effective city exploration with walking/biking focus, or asks "where should I go for a weekend?". Triggers on phrases like "穷游", "budget travel", "火车旅游", "省钱攻略", "周末去哪", "推荐目的地", or destination requests with cost concerns.
---

# Budget Travel China (中国穷游规划)

Plan cost-effective travel itineraries for mainland China with a focus on trains, shared bikes, hostels, and budget dining.

## Core Planning Steps

### Step 0: Determine Mode (Recommend vs Plan)

**If user has NO specific destination**:
- Enter **Recommendation Mode** (推荐模式)
- Ask: Time available? Departure city? Season/preferences?
- Consult `references/popular_destinations.md`
- Recommend 3-5 suitable destinations with:
  - Train duration and cost
  - **Day trip vs overnight** (based on distance)
  - Bike sharing status
  - Budget estimate
  - Why it's good for budget travel
- After user picks → Continue to Step 1

**If user has a specific destination**:
- Enter **Planning Mode** (规划模式)
- Continue to Step 1

---

### Step 0.5: Check if Day Trip is Better 🚄

**BEFORE planning accommodation**, evaluate if a day trip (当日往返) makes more sense:

**Day trip criteria** (三种模式):

**模式1：常规当日往返**
- Train time ≤ 1.5 hours one-way
- User has only 1-2 days available
- Destination is a city (not remote scenic area)
- Return: 20:00-22:00 (可玩到晚上，看夜景/吃晚餐)

**模式2：硬卧过夜当日游** ⭐ 穷游黑科技
- Train time: 8-10 hours (overnight sleeper berth)
- 晚上 22:00-23:00 出发 → 睡硬卧 → 早上 6:00-8:00 到达
- 优势：
  - ✅ 省住宿费（硬卧费用 = 交通费，但省了酒店 50-80 元）
  - ✅ 不浪费白天时间（睡觉时间在路上）
  - ✅ 早到早玩（可玩一整天 + 当晚返回 or 住一晚）
- 适用城市：
  - 北京 → 西安 (硬卧 ￥150, 8-9h)
  - 北京 → 青岛 (硬卧 ￥120, 9-10h)
  - 上海 → 厦门 (硬卧 ￥180, 10h)
  - 广州 → 桂林 (硬卧 ￥130, 9h)

**模式3：需要过夜**
- Train time > 2h (day trip) or > 10h (sleeper)
- 继续正常规划 (Step 1+)

**If YES → Day Trip Mode**:
- ✅ No accommodation cost (save 50-80 RMB)
- ✅ Early morning departure + late evening return (20:00-22:00)
- ✅ Focus on compact itinerary (1 day highlights)
- Budget: Train (round-trip) + food + local transport + tickets

**If YES → Sleeper Day Trip Mode** 🌙:
- ✅ Sleeper berth = transport + accommodation combined
- ✅ Arrive early morning, full day to explore
- ✅ Can return same night (hard mode) or stay 1 night (recommended)
- Budget: Sleeper (100-200) + food + local transport + tickets

**If NO → Overnight Trip Mode**:
- Continue with normal planning (Step 1+)

**Examples**:
- 北京 → 天津 (0.5-1h): ✅ 常规当日往返
- 北京 → 石家庄 (1-2h): ✅ 常规当日往返
- 北京 → 西安 (8-9h 硬卧): ✅ 硬卧过夜当日游
- 北京 → 青岛 (4-5h 高铁 / 9h 硬卧): ✅ 硬卧过夜当日游 or 过夜
- 上海 → 苏州 (1h): ✅ 常规当日往返

---

### Planning Mode Steps

1. **Check Bike Sharing Availability** 🚲
   - CRITICAL: Always check shared bikes; distinguish 🚲人力自行车 vs ⚡电助力自行车
   - 检测目标:
     - **御三家**: 美团🟡 / 哈啰🔵 / 青桔🟢
     - **政府公共自行车**: 杭州小红车、苏州好行、武汉公共自行车等
   - If NO pedal bikes → **Highlight clearly** and suggest bus/walking
   
   **检测方法: 交叉验证（Exa + 小红书）** ⭐
   
   运行一条命令即可完成双信源交叉验证：
   ```bash
   python3 scripts/check_bike_sharing.py 城市名
   # JSON 输出: python3 scripts/check_bike_sharing.py 城市名 --json
   ```
   
   脚本自动完成:
   1. **Exa 全网搜索** — 搜索"城市 共享单车"和"城市 公共自行车"
   2. **小红书实地反馈** — 搜索本地用户最新体验帖
   3. **交叉分析** — 综合两个信源，输出:
      - 御三家各品牌是否存在 + 车辆类型（人力/电助力）
      - 政府公共自行车是否存在 + 运营状况
      - 政府车的**外地注册便利性**（是否支持扫码、需否办卡/押金）
      - 政府车的**车辆维护评价**（用户反馈好/差）
      - 穷游出行建议
   
   **输出示例**:
   ```
   🟡 美团: ✅ 已检测到 | 车辆类型: ⚡ 电助力 | 置信度: 高
   🔵 哈啰: ✅ 已检测到 | 车辆类型: 🚲 人力 + ⚡ 电助力 | 置信度: 高
   政府公共自行车: 苏州好行 | 🚲 人力
     外地注册: 🟢 便捷 → 支持支付宝扫码
     车辆维护: 🟡 一般 → 评价不一
   ```
   
   **置信度规则**:
   - 高: 两个信源均有提及（交叉验证通过）
   - 中: 仅一个信源提及
   - 低: 信源不可用，结果不可靠
   
   **特殊案例** (已验证):
   - **杭州**: 主力是"小红车"（有桩），御三家基本无存在感
   - **苏州**: 有美团+哈啰，也有政府"苏州好行"
   
   **备选方法** (脚本不可用时):
   - 手动 Exa: `mcporter call 'exa.web_search_exa(query: "城市 共享单车", numResults: 5)'`
   - 手动小红书: `cd ~/.openclaw/skills/xiaohongshu-skills && uv run python scripts/cli.py search-feeds --keyword "城市 共享单车" --sort-by "最新"`
   - 高德 API: `python3 scripts/check_bike_realtime.py 城市名` (需 AMAP_API_KEY)
   **提示用户**: 无论结果如何，建议到站后打开 APP 再次确认

2. **Find Train Routes** 🚂
   - Long-distance: ONLY trains (普快/快车/高铁/动车)
   - NO flights (budget constraint)
   - Prioritize overnight trains (save accommodation cost)
   - Use `scripts/search_trains.py` to generate multi-platform search links:
     - 携程 (Ctrip) - price comparison, booking support
     - 飞猪 (Fliggy/Alitrip) - Alipay integration, coupons
     - 12306 official - authoritative, no fees (requires account)
     - 智行火车票 - best for ticket grabbing
   - Agent should present these links to user for manual booking
   - No actual booking API (requires user payment authorization)

3. **Plan Budget Accommodation** 🏨
   - Youth hostels (青旅) - 30-80 RMB/night
   - Budget guesthouses (小旅馆)
   - Capsule hotels where available
   - Check if hostel has bike rental (fallback if no shared bikes)

4. **Food Recommendations** 🍜
   - Local street food markets (小吃街)
   - Food courts (美食城)
   - University canteens (if accessible)
   - Avoid tourist trap restaurants
   - Budget: 30-60 RMB/day per person

5. **Check Weather Forecast** 🌤️
   - ALWAYS check weather for travel dates
   - Use wttr.in (no API key needed)
   ```bash
   curl -s "wttr.in/城市名?lang=zh&format=%l:+%c+%t+(体感+%f),+%w,+湿度+%h,+降水+%p"
   ```
   - Provide clothing/gear suggestions:
     - 雨天 → 带伞 🌂
     - 高温 (>30°C) → 防晒霜 + 遮阳帽 ☀️
     - 低温 (<10°C) → 羽绒服/冲锋衣 🧥
     - 大风 → 注意保暖
   - Seasonal alerts:
     - 春季：沙尘暴（北方）、春雨（南方）
     - 夏季：暴雨、台风（沿海）
     - 秋季：适合出行（最佳季节）
     - 冬季：雾霾（华北）、冰雪（东北）

6. **Attractions** 🏞️
   - Prioritize free/low-cost sites:
     - Parks and lakes (most are free)
     - Ancient town outskirts (免费区域)
     - University campuses
     - City walking routes
   - List student discounts where applicable

7. **Generate Itinerary**
   - **Day trip**: Use `assets/day_trip_template.md` (compact 1-day schedule)
   - **Overnight**: Use `assets/itinerary_template.md` (multi-day schedule)
   - Include:
     - Weather forecast for travel dates (wttr.in)
     - Daily schedule with walking/biking routes
     - Total cost breakdown (transport + accommodation + food + tickets)
     - Bike sharing instructions specific to that city
     - Clothing/gear suggestions based on weather
     - Money-saving tips

## Important Warnings

- **No Shared Bikes?** → Clearly state this upfront and emphasize walking + public bus
- **Government Public Bikes** → May require card deposit, explain registration process
- **Seasonal Considerations** → Warn about holiday price surges (春节/国庆/五一)

## Budget Calculation

**Day Trip** (当日往返):
- Train: Round-trip (往返) 50-200 RMB depending on distance
- Food: 50-80 RMB (breakfast at home, lunch+dinner outside)
- Local transport: 10-20 RMB (shared bikes + occasional bus)
- Attractions: 20-50 RMB
- **Total: ~150-300 RMB** (no accommodation cost!)

**Overnight Trip** (过夜):
Default daily budget per person:
- Accommodation: 50 RMB (hostel dorm)
- Food: 50 RMB
- Local transport: 10 RMB (mostly shared bikes)
- Attractions: 20-50 RMB
- **Total: ~150-180 RMB/day** (excluding long-distance train)

Adjust based on city tier (Tier 1 cities +30%, smaller cities -20%).

## Output Format

**For Day Trips** (当日往返):
1. 🚄 往返火车时刻 + 价格
2. 🚲 Bike sharing status
3. ⏰ 一日行程（紧凑安排）
4. 💰 Total cost estimate (无住宿费)
5. 💡 Day trip tips (早出晚归、带零食等)

**For Overnight Trips**:
Always include:
1. 🚲 Bike sharing status (FIRST THING)
2. 🚂 Recommended train routes with prices
3. 📅 Day-by-day itinerary
4. 💰 Total cost estimate
5. 💡 Money-saving tips specific to that destination

Consult `references/budget_tips.md` for proven cost-cutting strategies.
