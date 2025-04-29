import yfinance as yf
import pandas as pd
import requests
from datetime import datetime
import schedule
import time
import threading

# ———— 參數設定 ————
DISCORD_WEBHOOK_URL_DAILY = 'https://discord.com/api/webhooks/1366463100114567181/_ZNkB75cFx87ia4pgDJJUikujCWPkqOzMkZEVbDROqzfDt30atoospPsbeVrPbWnqRJk'
DISCORD_WEBHOOK_URL_5MIN  = 'https://discord.com/api/webhooks/1366463100114567181/_ZNkB75cFx87ia4pgDJJUikujCWPkqOzMkZEVbDROqzfDt30atoospPsbeVrPbWnqRJk'
SYMBOLS                  = ['2330.TW', 'TSM']

# 如果想要短名字，也可加這兩行：
DAILY_URL = DISCORD_WEBHOOK_URL_DAILY
MIN5_URL  = DISCORD_WEBHOOK_URL_5MIN

# ———— 推播函式、金叉邏輯同上 ————

def push_discord(text: str, webhook_url: str):
    resp = requests.post(webhook_url, json={"content": text})
    status = resp.status_code
    print(datetime.now(), f"Discord 推播狀態: {status}")

# ... fetch_ma, is_golden_cross, job() 都不變 ...

if __name__ == "__main__":
    # 首次執行
    job("2330.TW", DAILY_URL, "1d")
    job("2330.TW", MIN5_URL,  "5m")

    # 設定無限排程
    schedule.every().day.at("09:00").do( job, symbol="2330.TW", webhook_url=DAILY_URL, interval="1d" )
    schedule.every(5).minutes.do(   job, symbol="2330.TW", webhook_url=MIN5_URL,  interval="5m" )

    print("✅ 無限排程已啟動，按 Ctrl+C 停止。")
    while True:
        schedule.run_pending()
        time.sleep(1)
