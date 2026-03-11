#!/usr/bin/env python3
"""
共享单车实时检测工具 (Bike Sharing Real-time Checker)

功能：通过高德地图 Web 服务 API 检测目标城市是否有共享单车

使用方法：
1. 申请高德地图 Web 服务 API key (免费): https://console.amap.com/dev/key/app
2. 将 API key 保存到环境变量: export AMAP_API_KEY="your_key_here"
3. 运行脚本: python3 check_bike_realtime.py 城市名

依赖：pip3 install requests

数据来源：高德地图 POI 搜索 API
更新：2026-03-11
"""

import sys
import os
import json
import requests
from pathlib import Path

# 缓存文件路径
CACHE_FILE = Path(__file__).parent.parent / "references" / "bike_cache.json"

def load_cache():
    """加载本地缓存"""
    if CACHE_FILE.exists():
        with open(CACHE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_cache(cache):
    """保存缓存"""
    CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(CACHE_FILE, 'w', encoding='utf-8') as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)

def check_bike_amap(city, api_key):
    """
    通过高德地图 API 检测共享单车
    
    API 文档：https://lbs.amap.com/api/webservice/guide/api/search
    """
    base_url = "https://restapi.amap.com/v3/place/text"
    
    # 搜索关键词：美团单车、哈啰单车、青桔单车
    bike_brands = {
        "美团单车": "🟡",
        "哈啰单车": "🔵",
        "青桔单车": "🟢"
    }
    
    results = {}
    
    for brand, emoji in bike_brands.items():
        params = {
            "key": api_key,
            "keywords": brand,
            "city": city,
            "citylimit": "true",  # 仅搜索指定城市
            "offset": 1  # 只需要知道有没有，不需要详细列表
        }
        
        try:
            response = requests.get(base_url, params=params, timeout=5)
            data = response.json()
            
            if data.get("status") == "1":
                count = int(data.get("count", 0))
                results[brand] = {
                    "available": count > 0,
                    "count": count,
                    "emoji": emoji
                }
            else:
                print(f"⚠️  {brand} 查询失败: {data.get('info', '未知错误')}")
                results[brand] = {"available": False, "count": 0, "emoji": emoji}
                
        except Exception as e:
            print(f"⚠️  {brand} 网络请求失败: {e}")
            results[brand] = {"available": False, "count": 0, "emoji": emoji}
    
    return results

def format_result(city, results):
    """格式化输出结果"""
    print("=" * 50)
    print(f"城市：{city}")
    print("=" * 50)
    
    available_bikes = [brand for brand, info in results.items() if info["available"]]
    
    if available_bikes:
        print(f"\n✅ 有共享单车（{len(available_bikes)} 家）\n")
        for brand, info in results.items():
            if info["available"]:
                print(f"   {info['emoji']} {brand}: 有覆盖（检测到 {info['count']} 个停放点）")
        
        print(f"\n💡 建议：优先使用 {available_bikes[0]}（覆盖最广）")
        print("💡 提示：共享单车政策可能变化，建议到站后再次确认")
        
    else:
        print("\n❌ 未检测到御三家共享单车\n")
        print("   可能原因：")
        print("   1. 该城市确实没有企业共享单车")
        print("   2. 有地方政府公共自行车（需查询当地系统）")
        print("   3. API 数据未及时更新")
        print("\n💡 备选方案：")
        print("   - 查询地方公共自行车系统（如杭州小红车）")
        print("   - 使用公交卡")
        print("   - 询问青旅是否有自行车租赁")
    
    print("=" * 50)

def main():
    if len(sys.argv) < 2:
        print("用法: python3 check_bike_realtime.py 城市名")
        print("示例: python3 check_bike_realtime.py 成都")
        sys.exit(1)
    
    city = sys.argv[1]
    
    # 检查 API key
    api_key = os.environ.get("AMAP_API_KEY")
    if not api_key:
        print("❌ 未找到高德地图 API key")
        print("\n请按以下步骤配置：")
        print("1. 访问 https://console.amap.com/dev/key/app")
        print("2. 注册/登录，创建 Web 服务 API key（免费）")
        print("3. 设置环境变量:")
        print('   export AMAP_API_KEY="your_key_here"')
        print("\n暂时回退到静态数据库检测...\n")
        
        # 回退到静态数据库
        os.system(f"python3 {Path(__file__).parent}/check_bike_sharing.py {city}")
        sys.exit(0)
    
    # 检查缓存
    cache = load_cache()
    cache_key = f"{city}"
    
    if cache_key in cache:
        # 缓存有效期 7 天
        from datetime import datetime, timedelta
        cache_time = datetime.fromisoformat(cache[cache_key]["timestamp"])
        if datetime.now() - cache_time < timedelta(days=7):
            print(f"💾 使用缓存数据（{cache_time.strftime('%Y-%m-%d %H:%M')}）\n")
            format_result(city, cache[cache_key]["data"])
            return
    
    # 实时查询
    print(f"🔍 正在查询 {city} 的共享单车情况...\n")
    results = check_bike_amap(city, api_key)
    
    # 保存缓存
    from datetime import datetime
    cache[cache_key] = {
        "timestamp": datetime.now().isoformat(),
        "data": results
    }
    save_cache(cache)
    
    # 输出结果
    format_result(city, results)

if __name__ == "__main__":
    main()
