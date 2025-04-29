import requests
from datetime import datetime
import yfinance as yf
import pandas as pd

# ———— 設定 ————
TEST_MODE = True
TEST_WEBHOOK = "https://discord.com/api/webhooks/1366463100114567181/_ZNkB75cFx87ia4pgDJJUikujCWPkqOzMkZEVbDROqzfDt30atoospPsbeVrPbWnqRJk"
DISCORD_WEBHOOK_URL_DAILY = "https://discord.com/api/webhooks/1366463100114567181/_ZNkB75cFx87ia4pgDJJUikujCWPkqOzMkZEVbDROqzfDt30atoospPsbeVrPbWnqRJk"
DISCORD_WEBHOOK_URL_5MIN  = "https://discord.com/api/webhooks/1366463100114567181/_ZNkB75cFx87ia4pgDJJUikujCWPkqOzMkZEVbDROqzfDt30atoospPsbeVrPbWnqRJk"
DAILY_URL = TEST_MODE and TEST_WEBHOOK or DISCORD_WEBHOOK_URL_DAILY

# 最核心的推播函式
def push_discord(text: str, webhook_url: str):
    r = requests.post(webhook_url, json={"content": text})
    print(datetime.now(), "狀態:", r.status_code)

def job(symbol: str, url: str, interval: str):
    df = yf.Ticker(symbol).history(period="5d" if interval=="5m" else "60d",
                                   interval=interval)
    df["MA5"]  = df["Close"].rolling(5).mean()
    df["MA20"] = df["Close"].rolling(20).mean()
    y, t = df.iloc[-2], df.iloc[-1]
    status = "金叉！" if (y["MA5"]<=y["MA20"] and t["MA5"]>t["MA20"]) else "未金叉"
    text = f"{symbol} {interval} {status}"
    push_discord(text, url)

if __name__ == "__main__":
    # 1. 啟動時先跑一次（可省略）
    job("2330.TW", DAILY_URL, "1d")
    job("2330.TW", MIN5_URL, "5m")

    # 2. 設定排程：每分鐘/每 5 分鐘/每天固定時間都可以
    schedule.every(5).minutes.do(job, symbol="2330.TW", webhook_url=MIN5_URL, interval="5m")
    schedule.every().day.at("09:00").do(job, symbol="2330.TW", webhook_url=DAILY_URL, interval="1d")
    # 你也可以繼續加：
    # schedule.every(1).hours.do(...)
    # schedule.every().monday.do(...)

    # 3. 無限迴圈，持續檢查排程
    print("✅ 無限排程已啟動，按 Ctrl+C 停止。")
    while True:
        schedule.run_pending()
        time.sleep(1)
