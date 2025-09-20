import os
import csv
import sys
import json
import time
import math
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any

try:
    import requests
except ImportError:
    print("缺少 requests 包，请先安装: pip install requests")
    import sys as _sys
    _sys.exit(1)

# 说明：使用 Open-Meteo 免费历史接口 (ERA5 reanalysis) 来获取过去30天的小时级天气数据
# 文档：https://open-meteo.com/en/docs/historical-weather-api
# 优点：无需 API Key，速率限制较宽松；覆盖全球；包含温度、相对湿度、风速、天气现象编码。

OM_BASE = "https://archive-api.open-meteo.com/v1/era5"

# 输出列与现有 city_weather.csv 对齐
HEADER = ['city', 'lat', 'lon', 'time', 'temp', 'humidity', 'wind', 'wind_deg', 'weather']

WEATHER_CODE_MAP = {
    # Open-Meteo weathercode 映射到常见主类
    0: 'Clear',
    1: 'Clear', 2: 'Clouds', 3: 'Clouds',
    45: 'Fog', 48: 'Fog',
    51: 'Drizzle', 53: 'Drizzle', 55: 'Drizzle',
    56: 'Drizzle', 57: 'Drizzle',
    61: 'Rain', 63: 'Rain', 65: 'Rain',
    66: 'Rain', 67: 'Rain',
    71: 'Snow', 73: 'Snow', 75: 'Snow', 77: 'Snow',
    80: 'Rain', 81: 'Rain', 82: 'Rain',
    85: 'Snow', 86: 'Snow',
    95: 'Thunderstorm', 96: 'Thunderstorm', 99: 'Thunderstorm',
}


def parse_args():
    import argparse
    p = argparse.ArgumentParser(description='构建过去30天城市天气 (Open-Meteo ERA5)')
    p.add_argument('--cities-csv', default='city_weather.csv', help='包含城市、经纬度的CSV（读取 city/lat/lon）')
    p.add_argument('--out', default='city_weather.csv', help='输出CSV路径（将覆盖或追加）')
    p.add_argument('--append', action='store_true', help='若存在则追加，否则覆盖重建')
    p.add_argument('--days', type=int, default=30, help='回溯天数，默认30')
    p.add_argument('--cities-limit', type=int, default=None, help='仅抓取前N个城市用于测试')
    p.add_argument('--start', type=str, default=None, help='起始日期 YYYY-MM-DD（默认今天-天数）')
    p.add_argument('--end', type=str, default=None, help='结束日期 YYYY-MM-DD（默认今天-1）')
    p.add_argument('--tz', type=str, default='UTC', help='输出时间时区，默认 UTC (ISO 字符串)')
    return p.parse_args()


def load_cities(path: str) -> List[Dict[str, Any]]:
    cities = []
    with open(path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        # 要求至少 city, lat, lon 列
        for row in reader:
            try:
                name = row.get('city') or row.get('name')
                lat = float(row['lat'])
                lon = float(row['lon'])
            except Exception:
                # 可能是表头行或无效行
                continue
            cities.append({'city': name, 'lat': lat, 'lon': lon})
    # 去重（按 city,lat,lon）
    uniq = {}
    for c in cities:
        key = (c['city'], c['lat'], c['lon'])
        uniq[key] = c
    return list(uniq.values())


def daterange(days: int, start: str = None, end: str = None) -> tuple[str, str]:
    if start and end:
        return start, end
    today = datetime.now(timezone.utc).date()
    end_date = today - timedelta(days=1) if end is None else datetime.strptime(end, '%Y-%m-%d').date()
    start_date = end_date - timedelta(days=days-1) if start is None else datetime.strptime(start, '%Y-%m-%d').date()
    return start_date.isoformat(), end_date.isoformat()


def fetch_range(city: Dict[str, Any], start_date: str, end_date: str) -> List[Dict[str, Any]]:
    params = {
        'latitude': city['lat'],
        'longitude': city['lon'],
        'start_date': start_date,
        'end_date': end_date,
        'hourly': 'temperature_2m,relative_humidity_2m,wind_speed_10m,wind_direction_10m,weather_code',
        'timezone': 'UTC'
    }
    url = OM_BASE
    r = requests.get(url, params=params, timeout=30)
    r.raise_for_status()
    j = r.json()
    h = j.get('hourly') or {}
    times = h.get('time') or []
    temps = h.get('temperature_2m') or []
    hums = h.get('relative_humidity_2m') or []
    winds = h.get('wind_speed_10m') or []
    wdirs = h.get('wind_direction_10m') or []
    codes = h.get('weather_code') or []
    rows = []
    n = min(len(times), len(temps), len(hums), len(winds), len(wdirs), len(codes))
    for i in range(n):
        t_iso = times[i]
        # 规范为包含秒的 ISO 格式（Open-Meteo 小时级通常无秒）
        if len(t_iso) == 16:  # YYYY-MM-DDTHH:MM
            t_iso = t_iso + ":00"
        temp = temps[i]
        hum = hums[i]
        wind = winds[i]
        wdir = wdirs[i]
        code = int(codes[i]) if codes[i] is not None else None
        weather = WEATHER_CODE_MAP.get(code, 'Clouds' if code is not None else '')
        rows.append({
            'city': city['city'],
            'lat': city['lat'],
            'lon': city['lon'],
            'time': t_iso,
            'temp': temp,
            'humidity': hum,
            'wind': wind,
            'wind_deg': wdir,
            'weather': weather,
        })
    return rows


def write_rows(path: str, rows: List[Dict[str, Any]], append: bool):
    exists = os.path.isfile(path)
    mode = 'a' if append and exists else 'w'
    with open(path, mode, newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=HEADER)
        if mode == 'w':
            w.writeheader()
        for r in rows:
            w.writerow(r)


def main():
    args = parse_args()
    cities = load_cities(args.cities_csv)
    if args.cities_limit:
        cities = cities[: args.cities_limit]
    if not cities:
        print('未在 cities-csv 中找到城市/经纬度；请提供 city,lat,lon 列')
        sys.exit(1)
    start_date, end_date = daterange(args.days, args.start, args.end)
    print(f"抓取范围: {start_date} -> {end_date} | 城市数: {len(cities)}")
    all_rows: List[Dict[str, Any]] = []
    for idx, c in enumerate(cities, 1):
        try:
            rows = fetch_range(c, start_date, end_date)
            all_rows.extend(rows)
            print(f"[{idx}/{len(cities)}] {c['city']} ok: {len(rows)} 条")
            time.sleep(0.2)  # 轻微节流
        except Exception as e:
            print(f"[{idx}/{len(cities)}] {c['city']} 失败: {e}")
            time.sleep(0.5)
    # 写出
    write_rows(args.out, all_rows, append=args.append)
    print(f"完成: 写入 {len(all_rows)} 行 -> {args.out}")


if __name__ == '__main__':
    main()
