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
    # 快速在本機試一次，不用排程
    job("2330.TW", DAILY_URL, "1d")
    print("測試完成，不會進入無限排程。")
