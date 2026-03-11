#!/usr/bin/env python3
"""
Check bike sharing availability for a given city in China.
查询城市的共享单车覆盖情况
"""

import sys
import json

# 静态数据库（实际使用时可以从 API 或网页爬取更新）
BIKE_DATA = {
    # 有地方公共自行车的城市（一般不允许御三家）
    "public_bike_cities": {
        "杭州": {"system": "小红车", "method": "支付宝/办卡", "free_duration": "1小时"},
        "武汉": {"system": "武汉公共自行车", "method": "APP/办卡", "free_duration": "1小时"},
        "太原": {"system": "太原公共自行车", "method": "办卡", "free_duration": "1小时"},
        "苏州": {"system": "苏州好行", "method": "支付宝/APP", "free_duration": "1小时"},
        "常州": {"system": "永安行", "method": "APP", "free_duration": "1小时"},
        "绍兴": {"system": "绍兴公共自行车", "method": "办卡/扫码", "free_duration": "1小时"},
    },
    
    # 御三家覆盖的城市（企业共享单车）
    "corporate_bike_cities": {
        # 三家都有
        "full_coverage": [
            "北京", "上海", "广州", "深圳", "成都", "重庆", "西安", 
            "南京", "厦门", "青岛", "大连", "昆明", "贵阳", "长沙",
            "郑州", "济南", "福州", "合肥", "南昌", "石家庄"
        ],
        # 哈啰为主（下沉市场）
        "hellobike_dominant": [
            "东莞", "佛山", "珠海", "中山", "惠州", "江门",
            "温州", "宁波", "嘉兴", "台州", "金华", "绍兴"
        ],
    },
    
    # 基本无人力共享单车的城市
    "no_bike_cities": [
        "拉萨", "乌鲁木齐", "哈尔滨", "张家界", "九寨沟", "黄山",
        "丽江", "大理", "三亚", "桂林"  # 部分有电动车，但人力单车少
    ],
}

def check_city(city_name):
    """
    检查城市的共享单车情况
    返回结果字典
    """
    result = {
        "city": city_name,
        "has_bikes": False,
        "type": None,  # "public" / "corporate" / "none"
        "details": {},
        "warning": None
    }
    
    # 检查地方公共自行车
    if city_name in BIKE_DATA["public_bike_cities"]:
        result["has_bikes"] = True
        result["type"] = "public"
        result["details"] = BIKE_DATA["public_bike_cities"][city_name]
        result["details"]["note"] = "地方政府运营，御三家一般不进入该城市"
        return result
    
    # 检查企业共享单车
    if city_name in BIKE_DATA["corporate_bike_cities"]["full_coverage"]:
        result["has_bikes"] = True
        result["type"] = "corporate_full"
        result["details"] = {
            "providers": ["美团🟡", "哈啰🔵", "青桔🟢"],
            "coverage": "三家均有覆盖",
            "method": "扫码即用",
            "price": "约1.5-3元/30分钟"
        }
        return result
    
    if city_name in BIKE_DATA["corporate_bike_cities"]["hellobike_dominant"]:
        result["has_bikes"] = True
        result["type"] = "corporate_partial"
        result["details"] = {
            "providers": ["哈啰🔵（主要）", "美团🟡（部分）"],
            "coverage": "哈啰覆盖最好",
            "method": "扫码即用",
            "price": "约1.5-3元/30分钟"
        }
        return result
    
    # 检查无单车城市
    if city_name in BIKE_DATA["no_bike_cities"]:
        result["has_bikes"] = False
        result["type"] = "none"
        result["warning"] = f"⚠️ {city_name}基本无人力共享单车，建议使用公交卡+步行"
        result["details"] = {
            "alternative": "公交/出租车/步行",
            "reason": "地形不适合/偏远地区/依赖旅游大巴"
        }
        return result
    
    # 未知城市（数据库中没有）
    result["has_bikes"] = None
    result["type"] = "unknown"
    result["warning"] = f"⚠️ 数据库中无{city_name}的单车信息，建议实时查询美团/哈啰APP"
    result["details"] = {
            "suggestion": "打开美团/哈啰/青桔APP查看该城市是否有服务",
            "fallback": "提前联系青旅询问是否有自行车租赁"
        }
    return result

def print_result(result):
    """格式化打印结果"""
    print(f"\n{'='*50}")
    print(f"城市：{result['city']}")
    print(f"{'='*50}")
    
    if result["warning"]:
        print(f"\n{result['warning']}\n")
    
    if result["type"] == "public":
        print(f"✅ 有地方公共自行车")
        print(f"   系统名称：{result['details']['system']}")
        print(f"   使用方式：{result['details']['method']}")
        print(f"   免费时长：{result['details']['free_duration']}")
        print(f"   ⚠️ {result['details']['note']}")
    
    elif result["type"] == "corporate_full":
        print(f"✅ 有企业共享单车（御三家）")
        print(f"   运营商：{', '.join(result['details']['providers'])}")
        print(f"   覆盖情况：{result['details']['coverage']}")
        print(f"   使用方式：{result['details']['method']}")
        print(f"   参考价格：{result['details']['price']}")
    
    elif result["type"] == "corporate_partial":
        print(f"✅ 有企业共享单车（部分）")
        print(f"   运营商：{', '.join(result['details']['providers'])}")
        print(f"   覆盖情况：{result['details']['coverage']}")
        print(f"   使用方式：{result['details']['method']}")
        print(f"   参考价格：{result['details']['price']}")
    
    elif result["type"] == "none":
        print(f"❌ 无人力共享单车")
        print(f"   替代方案：{result['details']['alternative']}")
        print(f"   原因：{result['details']['reason']}")
    
    elif result["type"] == "unknown":
        print(f"❓ 数据未收录")
        print(f"   建议：{result['details']['suggestion']}")
        print(f"   备选：{result['details']['fallback']}")
    
    print(f"{'='*50}\n")

def main():
    if len(sys.argv) < 2:
        print("用法: python check_bike_sharing.py <城市名>")
        print("示例: python check_bike_sharing.py 杭州")
        sys.exit(1)
    
    city_name = sys.argv[1]
    result = check_city(city_name)
    
    # 如果有 --json 参数，输出 JSON
    if "--json" in sys.argv:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print_result(result)

if __name__ == "__main__":
    main()
