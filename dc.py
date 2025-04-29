import requests, schedule, time, yfinance as yf
from datetime import datetime
import pandas as pd
import os

DISCORD_WEBHOOK_URL = os.environ.get("https://discord.com/api/webhooks/1366463100114567181/_ZNkB75cFx87ia4pgDJJUikujCWPkqOzMkZEVbDROqzfDt30atoospPsbeVrPbWnqRJk")
SYMBOL = os.environ.get("SYMBOL", "2330.TW")

def fetch_ma(symbol: str) -> pd.DataFrame:
    df = yf.Ticker(symbol).history(period="30d")
    df["MA5"] = df["Close"].rolling(5).mean()
    df["MA20"] = df["Close"].rolling(20).mean()
    return df

def is_golden_cross(df: pd.DataFrame) -> bool:
    if len(df) < 2:
        return False
    yest = df.iloc[-2]
    today = df.iloc[-1]
    return yest["MA5"] <= yest["MA20"] and today["MA5"] > today["MA20"]

def push_discord(text: str):
    data = {"content": text}
    response = requests.post(DISCORD_WEBHOOK_URL, json=data)
    print(datetime.now(), "推播狀態:", response.status_code)

def job():
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    df = fetch_ma(SYMBOL)
    today = df.iloc[-1]
    status = "🎉 金叉發生！" if is_golden_cross(df) else "— 未發生金叉 —"
    text = (
        f"【{SYMBOL} 移動平均通知】\n"
        f"時間：{now}\n"
        f"5MA  = {today['MA5']:.2f}\n"
        f"20MA = {today['MA20']:.2f}\n"
        f"狀態：{status}"
    )
    push_discord(text)

if __name__ == "__main__":
    job()
    schedule.every(5).minutes.do(job)
    while True:
        schedule.run_pending()
        time.sleep(1)
