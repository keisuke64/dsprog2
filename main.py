import flet as ft
import requests
from datetime import datetime  # 日付フォーマット用


# 地域リストを取得する関数
def fetch_regions(): # 地域リストを取得する関数
    url = "http://www.jma.go.jp/bosai/common/const/area.json"
    try: # 例外処理
        response = requests.get(url) # GETリクエストを送信
        if response.status_code == 200: # ステータスコードが200の場合
            data = response.json() # レスポンスデータをJSON形式に変換
            regions = [
                (info["name"], code)
                for code, info in data["offices"].items()
            ] # 地域名と地域コードを取得
            return regions # 地域リストを返す
        else: # ステータスコードが200以外の場合
            print(f"Failed to fetch regions: {response.status_code}") # ステータスコードが200以外の場合
            return [] # 空のリストを返す
    except Exception as e: # 例外処理
        print(f"Error fetching regions: {e}") # エラーメッセージを表示
        return [] # 空のリストを返す


# 選択された地域の天気情報を取得する関数
def fetch_weather(region_code):
    url = f"https://www.jma.go.jp/bosai/forecast/data/forecast/{region_code}.json" 
    try:
        response = requests.get(url) # GETリクエストを送信
        if response.status_code == 200: # ステータスコードが200の場合
            return response.json() # レスポンスデータをJSON形式に変換して返す
        else: # ステータスコードが200以外の場合
            print(f"Failed to fetch weather: {response.status_code}") # エラーメッセージを表示
            return None 
    except Exception as e: # 例外処理
        print(f"Error fetching weather: {e}") # エラーメッセージを表示
        return None 


# 天気予報を解析する関数
def parse_weather_data(weather_data): 
    if not weather_data: # 天気データが存在しない場合
        return []  # 空のリストを返す

    try:
        forecasts = [] 
        # 予報データを抽出
        time_series = weather_data[0]["timeSeries"][0] 
        times = time_series["timeDefines"] 
        areas = time_series["areas"]

        for area in areas: # 各地域の天気情報を取得
            area_name = area["area"]["name"] 
            weathers = area["weathers"] 
            temps = area.get("temps", []) 

            for i, time in enumerate(times):
                # 日付を"MM/DD"に変換
                formatted_date = datetime.strptime(time.split("T")[0], "%Y-%m-%d").strftime("%m/%d")

                # 必要な情報を格納
                forecast = {
                    "date": formatted_date, # 日付
                    "area": area_name, # 地域名
                    "weather": weathers[i] if i < len(weathers) and weathers[i] else None, #天気
                    "temp": temps[i] if i < len(temps) and temps[i] else None #気温
                }
                forecasts.append(forecast) # 予報データをリストに追加

        return forecasts # 予報データを返す
    except KeyError as e: # キーが存在しない場合の例外処理
        print(f"KeyError: {e}") # エラーメッセージを表示
        return [] # 空のリストを返す


# アプリのメイン関数
def main(page: ft.Page):
    page.title = "気象庁天気予報アプリ"
    page.scroll = "adaptive"

    # 地域リストを取得
    regions = fetch_regions()

    # 天気予報表示コンテナ
    weather_container = ft.Column()

    # 地域が変更されたときの処理
    def on_region_change(e): 
        selected_region_code = e.control.value # 選択された地域コードを取得
        weather_container.controls.clear()  # 前のデータをクリア
        page.update()

        weather_data = fetch_weather(selected_region_code) # 天気情報を取得
        forecasts = parse_weather_data(weather_data) # 天気情報を解析

        if forecasts: # 天気情報が存在する場合
            for forecast in forecasts:
                # データがある要素だけを表示する
                content_controls = []

                if forecast["date"]: # 日付が存在する場合
                    content_controls.append(ft.Text(f"日付: {forecast['date']}", size=16, weight=ft.FontWeight.BOLD)) 

                if forecast["area"]: # 地域が存在する場合
                    content_controls.append(ft.Text(f"地域: {forecast['area']}", size=14))

                if forecast["weather"]: # 天気が存在する場合
                    content_controls.append(ft.Text(f"天気: {forecast['weather']}", size=14))

                if forecast["temp"]: # 気温が存在する場合
                    content_controls.append(ft.Text(f"気温: {forecast['temp']}℃", size=14))

                # データが存在する場合のみカードを作成
                if content_controls: # データが存在する場合
                    weather_container.controls.append( # 天気情報を表示
                        ft.Container( # コンテナを作成
                            content=ft.Column(  # カラムを作成
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
            weather_container.controls.append(ft.Text("エラーが発生しました")) # エラーメッセージを表示

        page.update()

    # 地域選択ドロップダウン
    region_dropdown = ft.Dropdown(
        label="地域を選択してください",
        options=[ft.dropdown.Option(text=name, key=code) for name, code in regions], # 地域リストをドロップダウンのオプションに変換
        on_change=on_region_change, # 地域が変更されたときの処理
    )

    # ページのレイアウト
    page.add( # ページに要素を追加
        ft.Column( # カラムを作成
            controls=[ # コントロールを追加
                region_dropdown, # 地域選択ドロップダウン
                ft.Divider(), # 区切り線
                weather_container # 天気予報表示コンテナ
            ],
        )
    )


# アプリの実行
ft.app(target=main)


