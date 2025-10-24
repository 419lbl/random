import pandas as pd, requests, schedule, time, os
from datetime import datetime
from io import StringIO

FINVIZ_API_KEY = "1d5ae8aa-5414-4fd5-8c08-bb12373c501d"
BASE = "https://elite.finviz.com/export.ashx"
PARAMS = f"v=111&o=-volume&p=1&auth={FINVIZ_API_KEY}"
URL = f"{BASE}?{PARAMS}"

SAVE_PATH = r"C:\Users\psim4\Desktop\Finviz_Snapshots"
os.makedirs(SAVE_PATH, exist_ok=True)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Accept": "text/csv",
}

def save_snapshot():
    now = datetime.now().strftime("%Y-%m-%d_%H-%M")
    try:
        r = requests.get(URL, headers=HEADERS, timeout=15)
        txt = r.text.strip("\ufeff").strip()        # remove BOM + whitespace

        if r.status_code == 200 and "Ticker" in txt:
            df = pd.read_csv(StringIO(txt))
            df.columns = df.columns.str.strip()

            if "Volume" in df.columns:
                df["Volume"] = (
                    df["Volume"]
                    .astype(str)
                    .str.replace(",", "", regex=False)
                    .astype(float)
                )
            df = df.head(20)

            path = os.path.join(SAVE_PATH, f"finviz_top20_by_volume_{now}.csv")
            df.to_csv(path, index=False)
            tickers = ", ".join(df["Ticker"].astype(str).head(8))
            print(f"✅ Snapshot saved: {path}")
            print(f"   Top tickers: {tickers}")
        else:
            print(f"⚠️ Response ok but header check skipped — saving anyway.")
            path = os.path.join(SAVE_PATH, f"finviz_raw_{now}.csv")
            with open(path, "w", encoding="utf-8") as f:
                f.write(txt)
            print(f"   Saved raw CSV: {path}")

    except Exception as e:
        print(f"❌ Exception: {e}")

save_snapshot()
schedule.every(2).minutes.do(save_snapshot)

print("📊 Finviz top-20-by-volume collector active (every 2 minutes)...")
while True:
    schedule.run_pending()
    time.sleep(10)
