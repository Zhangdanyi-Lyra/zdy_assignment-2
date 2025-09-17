# Animated Rainfall Map Project

本项目使用 Python 和 matplotlib 创建一个动画地图，展示过去100年每月平均降雨量，数据以彩色点的形式在地图上滚动显示。

## 主要依赖
- matplotlib
- numpy
- pandas
- basemap (或 cartopy)

## 运行方法
1. 安装依赖：
   ```bash
   pip install matplotlib numpy pandas basemap
   ```
2. 运行主程序：
   ```bash
   python animated_rainfall_map.py
   ```

## 数据说明
- 请将降雨量数据文件（如CSV）放在项目根目录，或根据代码注释调整数据路径。
- 示例数据结构：`year, month, lat, lon, rainfall`

## 主要文件
- `animated_rainfall_map.py`：主程序，包含动画实现。

---
如需自定义地图底图或数据格式，请参考代码注释进行调整。
>>>>>>> ee85071 (项目初次提交)
