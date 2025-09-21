
# Weather Data Visualization 0921

This folder contains all files required to reproduce the animated weather visualization:

- `world_weather_timeseries_map_wind.py`: Main Python script for generating the animation.
- `city_weather.csv`: Weather data for global cities (last 30 days).
- `outputs/weather_rays_len6_firework_tailfx.html`: Final animation output (HTML, open in browser).

## How to Run

Make sure you have Python 3 and the required packages installed (`pandas`, `numpy`, `plotly`).

Run the following command in this directory:

```bash
python world_weather_timeseries_map_wind.py \
	--input city_weather.csv \
	--out outputs/weather_rays_len6_firework_tailfx.html \
	--fps 12 --rays 10 --ray-undulate --ray-emit \
	--arrow-scale-km 40 --arrow-width-scale 0.4 \
	--firework --fw-trail --fw-core \
	--ray-length-mult 6.0 --ray-segments 8 --fw-expansion-km 440.0
```

Open the generated HTML file in your browser to view the animation.
