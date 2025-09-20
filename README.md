# Lyra Data Visualization

This workspace contains multiple Python visualizations. The primary weather animation script is now `world_weather_timeseries_map_wind.py` (hourly animation with wind arrows and stylized radiating curves). The legacy daily map script has been archived under `archive/world_weather_timeseries_map.py`.

## Quick Start

```bash
# Activate venv if needed
# source .venv/bin/activate

# Run the primary weather animation (hourly)
python world_weather_timeseries_map_wind.py --granularity hourly --hour-step 6 --fps 8 \
  --out outputs/world_weather_30d_wind_humidity_hourly.html
```

## Notes
- Data file: `city_weather.csv` (last 30 days, includes `wind_deg`).
- Mapbox token is optional; without it, humidity is rendered as semi-transparent points.
- See script `--help` for many styling flags (rays, glow, emission, tails, etc.).
