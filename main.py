import flet as ft
import requests
from datetime import datetime
import sqlite3


# データベース初期化
def init_db():
    conn = sqlite3.connect("weather.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS weather (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            area TEXT,
            weather TEXT,
            temp TEXT
        )
    """)
    conn.commit()
    conn.close()


# 天気データを保存
def save_weather_to_db(forecasts):
    conn = sqlite3.connect("weather.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM weather")
    for forecast in forecasts:
        cursor.execute("""
            INSERT INTO weather (date, area, weather, temp)
            VALUES (?, ?, ?, ?)
        """, (forecast["date"], forecast["area"], forecast["weather"], forecast["temp"]))
    conn.commit()
    conn.close()


# 天気データを取得
def get_weather_from_db():
    conn = sqlite3.connect("weather.db")
    cursor = conn.cursor()
    cursor.execute("SELECT date, area, weather, temp FROM weather")
    data = cursor.fetchall()
    conn.close()
    return [{"date": row[0], "area": row[1], "weather": row[2], "temp": row[3]} for row in data]


def fetch_regions():
    url = "http://www.jma.go.jp/bosai/common/const/area.json"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            return [(info["name"], code) for code, info in data["offices"].items()]
        else:
            print(f"Failed to fetch regions: {response.status_code}")
            return []
    except Exception as e:
        print(f"Error fetching regions: {e}")
        return []


def fetch_weather(region_code):
    url = f"https://www.jma.go.jp/bosai/forecast/data/forecast/{region_code}.json"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Failed to fetch weather: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error fetching weather: {e}")
        return None


def parse_weather_data(weather_data):
    if not weather_data:
        return []

    try:
        forecasts = []
        time_series = weather_data[0]["timeSeries"][0]
        times = time_series["timeDefines"]
        areas = time_series["areas"]

        for area in areas:
            area_name = area["area"]["name"]
            weathers = area["weathers"]
            temps = area.get("temps", [])

            for i, time in enumerate(times):
                formatted_date = datetime.strptime(time.split("T")[0], "%Y-%m-%d").strftime("%m/%d")
                forecasts.append({
                    "date": formatted_date,
                    "area": area_name,
                    "weather": weathers[i] if i < len(weathers) and weathers[i] else None,
                    "temp": temps[i] if i < len(temps) and temps[i] else None
                })

        return forecasts
    except KeyError as e:
        print(f"KeyError: {e}")
        return []


def main(page: ft.Page):
    init_db()

    page.title = "気象庁天気予報アプリ"
    page.scroll = "adaptive"

    regions = fetch_regions()
    weather_container = ft.Column()

    def on_region_change(e):
        selected_region_code = e.control.value
        weather_container.controls.clear()
        page.update()

        weather_data = fetch_weather(selected_region_code)
        forecasts = parse_weather_data(weather_data)

        if forecasts:
            save_weather_to_db(forecasts)
            forecasts_from_db = get_weather_from_db()
            for forecast in forecasts_from_db:
                content_controls = []

                if forecast["date"]:
                    content_controls.append(ft.Text(f"日付: {forecast['date']}", size=16, weight=ft.FontWeight.BOLD))

                if forecast["area"]:
                    content_controls.append(ft.Text(f"地域: {forecast['area']}", size=14))

                if forecast["weather"]:
                    content_controls.append(ft.Text(f"天気: {forecast['weather']}", size=14))

                if forecast["temp"]:
                    content_controls.append(ft.Text(f"気温: {forecast['temp']}℃", size=14))

                if content_controls:
                    weather_container.controls.append(
                        ft.Container(
                            content=ft.Column(
                                controls=content_controls,
                                spacing=5,
                            ),
                            border=ft.border.all(1, "black"),
                            padding=10,
                            margin=5,
                            width=400,
                        )
                    )
        else:
            weather_container.controls.append(ft.Text("エラーが発生しました"))

        page.update()

    region_dropdown = ft.Dropdown(
        label="地域を選択してください",
        options=[ft.dropdown.Option(text=name, key=code) for name, code in regions],
        on_change=on_region_change,
    )

    page.add(
        ft.Column(
            controls=[
                region_dropdown,
                ft.Divider(),
                weather_container
            ],
        )
    )


ft.app(target=main)
