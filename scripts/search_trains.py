#!/usr/bin/env python3
"""
Generate train search links for multiple platforms.
生成多平台火车票查询链接（携程、飞猪、12306）

使用方式：
python search_trains.py 北京 成都 2026-05-01
"""

import sys
import json
from datetime import datetime
from urllib.parse import quote

# 城市代码映射（部分常用城市）
CITY_CODES = {
    "北京": "BJP",
    "上海": "SHH",
    "广州": "GZQ",
    "深圳": "SZQ",
    "成都": "CDW",
    "重庆": "CQW",
    "西安": "XAY",
    "杭州": "HZH",
    "南京": "NJH",
    "武汉": "WHN",
    "长沙": "CSQ",
    "郑州": "ZZF",
    "天津": "TJP",
    "苏州": "SZH",
    "青岛": "QDK",
    "厦门": "XMS",
    "昆明": "KMM",
    "大连": "DLT",
    "济南": "JNK",
    "太原": "TYV",
}

def generate_search_links(from_city, to_city, date=None):
    """
    生成多平台查询链接
    """
    if not date:
        date = datetime.now().strftime("%Y-%m-%d")
    
    # 尝试获取城市代码（12306用）
    from_code = CITY_CODES.get(from_city, from_city)
    to_code = CITY_CODES.get(to_city, to_city)
    
    result = {
        "from": from_city,
        "to": to_city,
        "date": date,
        "links": {}
    }
    
    # 1. 携程火车票
    ctrip_date = date.replace("-", "")  # 20260501
    result["links"]["携程"] = {
        "url": f"https://trains.ctrip.com/TrainBooking/Search.aspx?from={quote(from_city)}&to={quote(to_city)}&date={ctrip_date}",
        "note": "携程火车票 - 支持比价、抢票、改签",
        "features": ["价格透明", "支持学生票", "可抢票"]
    }
    
    # 2. 飞猪（阿里旅行）
    result["links"]["飞猪"] = {
        "url": f"https://train.fliggy.com/booking/index.htm?from={quote(from_city)}&to={quote(to_city)}&date={date}",
        "note": "飞猪火车票 - 支付宝集成，常有优惠券",
        "features": ["支付宝集成", "信用免押", "优惠券"]
    }
    
    # 3. 12306 官方（需要城市代码，尽力而为）
    result["links"]["12306官方"] = {
        "url": f"https://kyfw.12306.cn/otn/leftTicket/init?linktypeid=dc&fs={from_code}&ts={to_code}&date={date}&flag=N,N,Y",
        "note": "12306官网 - 官方渠道，最权威",
        "features": ["官方数据", "无手续费", "最可靠"],
        "warning": "需要注册账号并登录"
    }
    
    # 4. 智行火车票（深度链接，移动端）
    result["links"]["智行火车票"] = {
        "url": f"https://m.suanya.com/train/queryTrainList?from={quote(from_city)}&to={quote(to_city)}&date={date}",
        "note": "智行火车票APP - 抢票成功率高",
        "features": ["抢票功能强", "自动候补", "到票提醒"],
        "tip": "建议下载APP使用"
    }
    
    return result

def print_result(result):
    """格式化打印结果"""
    print(f"\n{'='*70}")
    print(f"🚂 火车票查询：{result['from']} → {result['to']}")
    print(f"📅 日期：{result['date']}")
    print(f"{'='*70}\n")
    
    print("🔗 点击以下链接查询和购票：\n")
    
    for platform, info in result["links"].items():
        print(f"【{platform}】")
        print(f"   链接：{info['url']}")
        print(f"   说明：{info['note']}")
        print(f"   特色：{' | '.join(info['features'])}")
        if "warning" in info:
            print(f"   ⚠️  {info['warning']}")
        if "tip" in info:
            print(f"   💡 {info['tip']}")
        print()
    
    print(f"{'='*70}")
    print("📌 使用建议：")
    print("   1. 【比价】先看携程/飞猪价格（含服务费）")
    print("   2. 【购票】如果价格一样，优先12306官网（无手续费）")
    print("   3. 【抢票】热门线路用智行火车票APP")
    print("   4. 【优惠】飞猪常有新用户券，可以关注")
    print(f"{'='*70}\n")
    
    print("💡 穷游小贴士：")
    print("   - 提前15-30天买票（越早越便宜）")
    print("   - 工作日比周末便宜")
    print("   - 硬卧下铺 > 硬座过夜（省一晚住宿）")
    print("   - 学生证打7.5折（务必使用）")
    print()

def main():
    if len(sys.argv) < 3:
        print("用法: python search_trains.py <出发城市> <到达城市> [日期]")
        print("示例: python search_trains.py 北京 成都 2026-05-01")
        print("\n生成携程、飞猪、12306等平台的查询链接")
        sys.exit(1)
    
    from_city = sys.argv[1]
    to_city = sys.argv[2]
    date = sys.argv[3] if len(sys.argv) > 3 else None
    
    result = generate_search_links(from_city, to_city, date)
    
    # 如果有 --json 参数，输出 JSON
    if "--json" in sys.argv:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print_result(result)

if __name__ == "__main__":
    main()
