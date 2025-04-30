import yfinance as yf
import pandas as pd
import requests, json
from datetime import datetime
import schedule
import time
import threading
import os

# ———— 參數設定 ————
DISCORD_WEBHOOK_URL_DAILY = 'https://discord.com/api/webhooks/1366463100114567181/_ZNkB75cFx87ia4pgDJJUikujCWPkqOzMkZEVbDROqzfDt30atoospPsbeVrPbWnqRJk'
DISCORD_WEBHOOK_URL_5MIN = 'https://discord.com/api/webhooks/1366465811601948732/IklK1oYEDjxdNFO8feCF_C_GaozZ96OpZbZx_8GzRUT8CTBWeOMJqqCPZu035sHWpgof'
SYMBOLS = ['2330.TW', 'TSM']  # 要監控的多支股票

# ———— 共用函式 ————
def push_discord(text: str, webhook_url: str):
    data = {"content": text}
    resp = requests.post(webhook_url, json=data)
    if resp.status_code in [200, 204]:
        print(datetime.now(), "Discord push 成功")
    else:
        print(datetime.now(), f"Discord push 失敗，狀態碼: {resp.status_code}, 回應: {resp.text}")

def fetch_ma(symbol: str, interval: str) -> pd.DataFrame:
    if interval == "1d":
        df = yf.Ticker(symbol).history(period="60d", interval="1d")
    elif interval == "5m":
        df = yf.download(symbol, period="3d", interval="5m", progress=False)
    else:
        raise ValueError("Unsupported interval")
    
    df["MA5"]  = df["Close"].rolling(5).mean()
    df["MA20"] = df["Close"].rolling(20).mean()

    # 確保資料有 MA5 和 MA20 欄位
    if "MA5" not in df.columns or "MA20" not in df.columns:
        raise ValueError(f"Data for {symbol} is missing 'MA5' or 'MA20' columns.")
    
    return df

# 修正金叉邏輯：避免錯誤 "The truth value of a Series is ambiguous"
def is_golden_cross(df: pd.DataFrame) -> bool:
    if len(df) < 2:
        return False
    yesterday = df.iloc[-2]
    today     = df.iloc[-1]
    return (yesterday["MA5"] <= yesterday["MA20"]).item() and (today["MA5"] > today["MA20"]).item()

# ———— 任務函式 ————
def job(symbol: str, webhook_url: str, interval: str):
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    try:
        df  = fetch_ma(symbol, interval)
        today = df.iloc[-1]
        # 確保 today["MA5"] 和 today["MA20"] 是數值而不是 Series
        ma5_value = today["MA5"].item()
        ma20_value = today["MA20"].item()
        status = "⚡ **金叉發生！**" if is_golden_cross(df) else "— 未發生金叉 —"
        text = (
            f"【{symbol} {interval} 移動平均通知】\n"
            f"時間：{now}\n"
            f"5MA  = {ma5_value:.2f}\n"
            f"20MA = {ma20_value:.2f}\n"
            f"狀態：{status}"
        )
        push_discord(text, webhook_url)
    except ValueError as e:
        print(f"錯誤: {e}, 股票: {symbol}, 時間: {now}")

# ———— 主程式 ————
stop_event = threading.Event()

def wait_for_stop():
    input("按下 Enter 鍵以停止推播...\n")
    stop_event.set()

if __name__ == "__main__":
    # 讓使用者輸入間隔時間

    interval_5min = 5
    interval_daily = 60

    # 啟動停止監聽執行緒
    threading.Thread(target=wait_for_stop, daemon=True).start()

    # 排程設定：每股票一個任務，分開日K和5分鐘K
    for symbol in SYMBOLS:
        # 日K推播任務
        schedule.every(interval_daily).minutes.do(job, symbol=symbol, webhook_url=DISCORD_WEBHOOK_URL_DAILY, interval="1d")
        # 5分鐘K推播任務
        schedule.every(interval_5min).minutes.do(job, symbol=symbol, webhook_url=DISCORD_WEBHOOK_URL_5MIN, interval="5m")

    # 先執行一次
    for symbol in SYMBOLS:
        job(symbol, DISCORD_WEBHOOK_URL_DAILY, "1d")
        job(symbol, DISCORD_WEBHOOK_URL_5MIN, "5m")

    # 主循環
    while not stop_event.is_set():
        schedule.run_pending()
        time.sleep(1)

    print("停止推播。")
