from collections import defaultdict
from datetime import datetime
import os
import requests
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

load_dotenv()

mcp = FastMCP("Weather MCP Server")


OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")


@mcp.tool()
def get_current_weather(city: str):
    """Fetch current instantaneous weather observations for a city."""
    response = requests.get(
        "https://api.openweathermap.org/data/2.5/weather",
        params={
            "q": city,
            "appid": OPENWEATHER_API_KEY,
            "units": "metric"
        }
    )

    data = response.json()

    if response.status_code != 200:
        return data

    return {
        "city": data.get("name", city),
        "temperature_c": data.get("main", {}).get("temp"),
        "feels_like_c": data.get("main", {}).get("feels_like"),
        "humidity": data.get("main", {}).get("humidity"),
        "condition": data.get("weather", [{}])[0].get("description", ""),
        "wind_speed": data.get("wind", {}).get("speed"),
    }


@mcp.tool()
def get_forecast(city: str):
    """Fetch multi-day meteorological forecast aggregated by calendar day for a city."""
    url = "https://api.openweathermap.org/data/2.5/forecast"

    params = {
        "q": city,
        "appid": OPENWEATHER_API_KEY,
        "units": "metric"
    }

    response = requests.get(
        url,
        params=params
    )

    data = response.json()

    if response.status_code != 200:
        return data

    daily_data = defaultdict(lambda: {"temps": [], "conditions": [], "humidities": [], "rain_chances": []})

    for item in data.get("list", []):
        dt_txt = item.get("dt_txt", "")
        date_str = dt_txt.split(" ")[0] if " " in dt_txt else dt_txt[:10]
        if not date_str:
            continue

        temp = item.get("main", {}).get("temp")
        if temp is not None:
            daily_data[date_str]["temps"].append(temp)

        humidity = item.get("main", {}).get("humidity")
        if humidity is not None:
            daily_data[date_str]["humidities"].append(humidity)

        weather_list = item.get("weather", [])
        if weather_list and "description" in weather_list[0]:
            daily_data[date_str]["conditions"].append(weather_list[0]["description"])

        pop = item.get("pop", 0)
        daily_data[date_str]["rain_chances"].append(pop)

    daily_forecast = []
    for date_str, values in daily_data.items():
        temps = values["temps"]
        if not temps:
            continue
        t_min = round(min(temps), 1)
        t_max = round(max(temps), 1)
        t_avg = round(sum(temps) / len(temps), 1)

        conds = values["conditions"]
        common_cond = max(set(conds), key=conds.count) if conds else ""

        avg_humidity = round(sum(values["humidities"]) / len(values["humidities"])) if values["humidities"] else None
        max_rain_prob = round(max(values["rain_chances"]) * 100) if values["rain_chances"] else 0

        try:
            day_name = datetime.strptime(date_str, "%Y-%m-%d").strftime("%A")
        except Exception:
            day_name = ""

        day_dict = {
            "date": date_str,
            "day": day_name,
            "temperature": t_avg,
            "temp_min": t_min,
            "temp_max": t_max,
            "weather": common_cond.capitalize() if common_cond else "",
            "rain_probability": max_rain_prob,
        }
        if avg_humidity is not None:
            day_dict["humidity"] = avg_humidity

        daily_forecast.append(day_dict)

    forecast_start = daily_forecast[0]["date"] if daily_forecast else ""
    forecast_end = daily_forecast[-1]["date"] if daily_forecast else ""

    return {
        "city": city,
        "forecast_start": forecast_start,
        "forecast_end": forecast_end,
        "daily_forecast": daily_forecast,
        "forecast": daily_forecast,
    }


if __name__ == "__main__":
    mcp.run()
